"use client";
import React, { useEffect, useState, useRef } from "react";
import * as SpeechSDK from "microsoft-cognitiveservices-speech-sdk";
import { configurationApi, avatarEngine } from "@/utils/api";
import { FaMicrophone, FaMicrophoneSlash, FaChevronDown } from "react-icons/fa";
import AvatarUserVideo from "./AvatarUserVideo";
import type { Case } from "@/types/cases";

const speechKey = process.env.NEXT_PUBLIC_SPEECH_KEY || "";
const speechRegion = process.env.NEXT_PUBLIC_SPEECH_REGION || "";

type AvatarConfig = {
  character: string;
  style: string;
  videoFormat: SpeechSDK.AvatarVideoFormat;
};

class AvatarHandler {
  public speechConfig: SpeechSDK.SpeechConfig;
  private avatarConfig: SpeechSDK.AvatarConfig;
  private peerConnection!: RTCPeerConnection;
  private avatarSynthesizer!: SpeechSDK.AvatarSynthesizer;
  private speechRecognizer!: SpeechSDK.SpeechRecognizer;
  private isSessionActive: boolean = false;
  public onVideoStream?: (stream: MediaStream) => void;

  constructor(config: AvatarConfig) {
    const speechConfig = SpeechSDK.SpeechConfig.fromSubscription(speechKey, speechRegion);

    speechConfig.speechSynthesisLanguage = "pt-BR";
    speechConfig.speechSynthesisVoiceName = "pt-BR-AntonioNeural";

    this.speechConfig = speechConfig;
    this.avatarConfig = new SpeechSDK.AvatarConfig(config.character, config.style, config.videoFormat);
  }

  public updateLanguage(language: string, voice: string) {
    this.speechConfig.speechSynthesisLanguage = language;
    this.speechConfig.speechSynthesisVoiceName = voice;
    console.log(`Updated TTS language to ${language} and voice to ${voice}`);
  }

  private async fetchIceServers(): Promise<RTCIceServer[]> {
    const response = await fetch(
      `https://${speechRegion}.tts.speech.microsoft.com/cognitiveservices/avatar/relay/token/v1`,
      {
        method: "GET",
        headers: {
          "Ocp-Apim-Subscription-Key": speechKey,
        },
      }
    );

    if (!response.ok) {
      console.error("Failed to fetch ICE server information:", response);
      throw new Error("Failed to fetch ICE server information");
    }

    console.log("ICE server information fetched successfully. \nResponse: ", response);

    const data = await response.json();

    return data.Urls.map((url: string) => ({
      urls: url,
      username: data.Username,
      credential: data.Password,
    }));
  }

  private async initializePeerConnection() {
    if (this.isSessionActive) {
      console.log("Avatar session is already active.");
      return this.peerConnection;
    }

    const iceServers = await this.fetchIceServers();
    this.peerConnection = new RTCPeerConnection({ iceServers });

    this.peerConnection.addTransceiver("video", { direction: "sendrecv" });
    this.peerConnection.addTransceiver("audio", { direction: "sendrecv" });

    this.isSessionActive = true;
    return this.peerConnection;
  }

  public async startAvatar(videoRef: React.RefObject<HTMLDivElement>) {
    if (this.isSessionActive) {
      console.log("Avatar session is already running.");
      return;
    }

    const peerConnection = await this.initializePeerConnection();

    console.log(`Spoken language: ${this.speechConfig.speechSynthesisLanguage || "not set"}`);

    this.avatarSynthesizer = new SpeechSDK.AvatarSynthesizer(this.speechConfig, this.avatarConfig);
    this.avatarSynthesizer.avatarEventReceived = (s, e) => {
      const offsetMessage = e.offset ? `, offset from session start: ${e.offset / 10000}ms.` : "";
      console.log(`Event received: ${e.description}${offsetMessage}`);
    };

    peerConnection.ontrack = (event) => {
      console.log("Track event received:", event);
      if (event.track.kind === "audio") {
        console.log("Audio track received from the avatar.");
        const audioElement = document.createElement("audio");
        audioElement.id = "audioPlayer";
        audioElement.srcObject = event.streams[0];
        audioElement.autoplay = true;
        audioElement.className = "hidden";

        audioElement.controls = true;

        document.body.appendChild(audioElement);
      }
      if (event.track.kind === "video" && this.onVideoStream) {
        this.onVideoStream(event.streams[0]);
      }
    };

    await this.avatarSynthesizer.startAvatarAsync(peerConnection);
    console.log("Avatar session started.");
  }

  public async getAvatarResponse(spokenText: string, chatHistory: string, chatId: Case) {
    if (!chatId?.id) {
      console.error("No case ID provided");
      return null;
    }
    
    try {
      const response = await avatarEngine.post("/response", {
        prompt: spokenText,
        chat_history: chatHistory,
        case_id: chatId.id
      });

      if (response.status === 200 || response.status === 201) {
        console.log("Avatar response:", response?.data?.text);
        return response?.data?.text;
      } else {
        console.error("Error occurred while getting avatar response.");
        return null;
      }
    } catch (error) {
      console.error("Error getting avatar response:", error);
      return "Error processing your request.";
    }
  }

  public async chat(spokenText: string) {
    if (!this.avatarSynthesizer) {
      throw new Error("Avatar Synthesizer is not initialized.");
    }

    const ssml = `<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="${this.speechConfig.speechSynthesisLanguage}">
      <voice name="${this.speechConfig.speechSynthesisVoiceName}">${spokenText}</voice>
    </speak>`;

    try {
      await this.avatarSynthesizer.speakSsmlAsync(ssml).then((result) => {
        if (result.reason === SpeechSDK.ResultReason.SynthesizingAudioCompleted) {
          console.log("Speech and avatar synthesized successfully.");
        } else if (result.reason === SpeechSDK.ResultReason.Canceled) {
          const cancellationDetails = SpeechSDK.CancellationDetails.fromResult(result as SpeechSDK.SpeechSynthesisResult);
          console.error("Speech synthesis canceled:", cancellationDetails.errorDetails);
        }
      });
    } catch (error) {
      console.error("Failed to synthesize speech:", error);
    }
  }

  public stopAvatar() {
    try {
      if (this.avatarSynthesizer) {
        this.avatarSynthesizer.close();
        console.log("Avatar synthesizer closed successfully.");
      }

      if (this.peerConnection) {
        this.peerConnection.close();
        console.log("WebRTC peer connection closed.");
      }

      this.isSessionActive = false;
      console.log("Avatar session disconnected.");
    } catch (error) {
      console.error("Error disconnecting avatar session:", error);
    }
  }

  public startMicrophone(onRecognized: (text: string) => void, language: string) {
    const audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
    this.speechRecognizer = new SpeechSDK.SpeechRecognizer(this.speechConfig, audioConfig);

    this.speechRecognizer.recognized = (s, e) => {
      if (e.result.reason === SpeechSDK.ResultReason.RecognizedSpeech) {
        console.log("Recognized text:", e.result.text);
        onRecognized(e.result.text);
      }
    };

    this.speechConfig.speechRecognitionLanguage = language;
    console.log(`Updated STT recognition language to ${language}`);

    this.speechRecognizer.startContinuousRecognitionAsync(
      () => console.log("Microphone recognition started."),
      (error) => console.error("Failed to start microphone recognition:", error)
    );
  }

  public stopMicrophone() {
    if (this.speechRecognizer) {
      this.speechRecognizer.stopContinuousRecognitionAsync(
        () => console.log("Microphone recognition stopped."),
        (error) => console.error("Failed to stop microphone recognition:", error)
      );
    }
  }
}

const AvatarChat: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const videoRef = useRef<HTMLDivElement>(null);
  const [spokenText, setSpokenText] = useState("");
  const avatarHandlerRef = useRef<AvatarHandler | null>(null);
  const [isMicrophoneActive, setIsMicrophoneActive] = useState(true);
  const [chatHistory, setChatHistory] = useState<Array<{ user?: string; assistant?: string }>>([]);
  const [availableCases, setAvailableCases] = useState<Case[]>([]);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcriptText, setTranscriptText] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [avatarVideoStream, setAvatarVideoStream] = useState<MediaStream | null>(null);

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const response = await avatarEngine.get("/cases/");
        if (response.status === 200) {
          setAvailableCases(response.data.result || []);
        }
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        setError("Error fetching available cases: " + msg);
        console.error("Error fetching available cases:", err);
      }
    };

    fetchCases();
  }, []);

  useEffect(() => {
    if (!avatarHandlerRef.current) {
      avatarHandlerRef.current = new AvatarHandler({
        character: "harry",
        style: "casual",
        videoFormat: new SpeechSDK.AvatarVideoFormat("H264", 2000000, 1920, 1080),
      });
    }
  }, []);

  useEffect(() => {
    const setupAvatar = async () => {
      if (!selectedCase || !videoRef.current || !avatarHandlerRef.current) return;

      setIsLoading(true);
      setError(null);
      setAvatarVideoStream(null); // Reset video stream
      try {
        const gender = selectedCase?.profile?.gender || "male";
        const language = "pt-BR";
        const voice = gender === "feminino" ? "pt-BR-FranciscaNeural" : "pt-BR-AntonioNeural";

        avatarHandlerRef.current.speechConfig.speechSynthesisLanguage = language;
        avatarHandlerRef.current.speechConfig.speechSynthesisVoiceName = voice;

        avatarHandlerRef.current.onVideoStream = (stream: MediaStream) => {
          setAvatarVideoStream(stream);
        };

        await avatarHandlerRef.current.startAvatar(videoRef);

        setChatHistory([]);

        console.log(`Avatar started with language ${language} and voice ${voice}`);
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        setError("Failed to set up avatar: " + msg);
        console.error("Failed to set up avatar:", err);
      } finally {
        setIsLoading(false);
      }
    };

    setupAvatar();
  }, [selectedCase]);

  useEffect(() => {
    if (!avatarHandlerRef.current || !selectedCase) return;

    const processTranscript = async (text: string) => {
      if (text.trim() === "" || isSpeaking) return;

      setTranscriptText(text);

      const updatedHistory = [...chatHistory, { user: text }];
      setChatHistory(updatedHistory);

      setIsSpeaking(true);
      try {
        const response = await avatarHandlerRef.current?.getAvatarResponse(
          text,
          JSON.stringify(chatHistory),
          selectedCase
        );

        if (response) {
          setChatHistory((prev) => [...prev, { assistant: response }]);
          await avatarHandlerRef.current?.chat(response);
        }
      } catch (error) {
        console.error("Error processing avatar response:", error);
      } finally {
        setIsSpeaking(false);
        setTranscriptText("");
      }
    };

    if (isMicrophoneActive) {
      avatarHandlerRef.current.startMicrophone((text) => {
        processTranscript(text);
      }, "pt-BR");
    } else {
      avatarHandlerRef.current.stopMicrophone();
    }

    return () => {
      if (avatarHandlerRef.current) {
        avatarHandlerRef.current.stopMicrophone();
      }
    };
  }, [isMicrophoneActive, selectedCase, chatHistory, isSpeaking]);
  return (
    <div className="flex flex-col w-full h-full relative">
      <div className="sticky top-0 z-20 bg-white dark:bg-boxdark bg-opacity-95 py-4 mb-4 backdrop-blur-sm">
        <form className="flex items-center gap-3 w-full max-w-xl mx-auto px-4">
          <div className="relative flex-1">
            <FaChevronDown className="absolute left-4 top-1/2 transform -translate-y-1/2 text-cyan-600 text-xl" />
            <select
              className="w-full rounded-xl border-2 border-cyan-200 px-10 py-3 text-lg focus:border-green-400 focus:ring-2 focus:ring-green-200 bg-white dark:bg-boxdark shadow-sm"
              value={selectedCase?.id || ""}
              onChange={(e) => {
                const found = availableCases.find((c) => c.id === e.target.value);
                setSelectedCase(found || null);
              }}
            >
              <option value="" disabled>
                Select a case to start...
              </option>
              {availableCases.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
        </form>
      </div>

      <div className="flex flex-col items-center w-full px-4 md:px-8 relative">
        {error && (
          <div className="w-full max-w-2xl mx-auto bg-red-100 text-red-800 border border-red-300 rounded-lg p-4 mb-4">
            <strong>Error:</strong> {error}
          </div>
        )}
        {isLoading ? (
          <div className="w-full h-[70vh] flex flex-col items-center justify-center">
            <div className="w-24 h-24 border-4 border-cyan-600 border-t-transparent rounded-full animate-spin mb-4"></div>
            <div className="text-2xl text-cyan-600 font-medium">Loading avatar...</div>
          </div>
        ) : (
          <div ref={videoRef} className="w-full h-[70vh] rounded-xl bg-gradient-to-b from-gray-50 to-cyan-50 dark:from-boxdark dark:to-gray-800 shadow-xl flex items-center justify-center overflow-hidden">
            {avatarVideoStream ? (
              <video
                autoPlay
                playsInline
                muted={false}
                ref={el => {
                  if (el && avatarVideoStream) {
                    el.srcObject = avatarVideoStream;
                  }
                }}
                className="w-full h-full object-contain rounded-xl"
              />
            ) : !selectedCase ? (
              <div className="text-center p-8">
                <div className="text-6xl text-gray-300 dark:text-gray-600 mb-4">👤</div>
                <div className="text-2xl text-gray-500 dark:text-gray-400">Select a case to start</div>
                <p className="text-gray-400 dark:text-gray-500 mt-2 max-w-md">
                  Choose from available cases to begin your avatar interaction experience
                </p>
              </div>
            ) : null}
          </div>
        )}

        {/* Chat History Panel */}
        {chatHistory.length > 0 && (
          <div className="mt-6 w-full max-w-4xl mx-auto bg-white dark:bg-boxdark rounded-xl shadow-md p-4 max-h-[30vh] overflow-y-auto">
            <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-3 border-b pb-2">Conversation History</h3>
            <div className="space-y-4">
              {chatHistory.map((msg, index) => (
                <div key={index} className="flex flex-col">
                  {msg.user && (
                    <div className="flex items-start mb-2">
                      <div className="bg-blue-100 dark:bg-blue-900 rounded-lg py-2 px-4 max-w-[80%] text-gray-800 dark:text-gray-200">
                        <p>{msg.user}</p>
                      </div>
                    </div>
                  )}
                  {msg.assistant && (
                    <div className="flex items-start self-end">
                      <div className="bg-green-100 dark:bg-green-900 rounded-lg py-2 px-4 max-w-[80%] text-gray-800 dark:text-gray-200">
                        <p>{msg.assistant}</p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="fixed bottom-24 left-1/2 transform -translate-x-1/2 flex flex-col items-center z-10">
          {transcriptText && (
            <div className="mb-6 p-4 bg-white dark:bg-boxdark rounded-lg border border-cyan-200 shadow-lg max-w-lg">
              <p className="text-sm font-medium text-cyan-600 dark:text-cyan-400 mb-1">Transcribing...</p>
              <p className="text-lg">{transcriptText}</p>
            </div>
          )}

          <button
            onClick={() => setIsMicrophoneActive((prev) => !prev)}
            disabled={!selectedCase}
            className={`p-6 rounded-full shadow-lg text-white text-4xl transition-all transform hover:scale-105 ${
              !selectedCase
                ? "bg-gray-400 cursor-not-allowed opacity-50"
                : isMicrophoneActive
                ? "bg-green-500 hover:bg-green-600 ring-4 ring-green-200 dark:ring-green-900"
                : "bg-red-500 hover:bg-red-600 ring-4 ring-red-200 dark:ring-red-900"
            }`}
            title={isMicrophoneActive ? "Disable Microphone" : "Enable Microphone"}
          >
            {isMicrophoneActive ? <FaMicrophone /> : <FaMicrophoneSlash />}
          </button>
          <span className="mt-4 text-lg font-semibold text-white bg-black bg-opacity-60 px-4 py-2 rounded-full">
            {!selectedCase
              ? "Select a case first"
              : isMicrophoneActive
              ? "Microphone Active - Speak Now"
              : "Microphone Disabled"}
          </span>
        </div>
      </div>

      {selectedCase && (
        <div className="absolute top-24 right-8 bg-white dark:bg-boxdark p-4 rounded-xl shadow-xl border border-gray-100 dark:border-gray-700 max-w-xs">
          <h3 className="text-lg font-bold text-cyan-700 dark:text-cyan-500 mb-3 border-b border-gray-200 dark:border-gray-700 pb-2">
            Active Case
          </h3>
          <div className="space-y-2">
            <p className="flex items-center">
              <span className="font-medium w-24">Name:</span> 
              <span className="flex-1">{selectedCase.name}</span>
            </p>
            <p className="flex items-center">
              <span className="font-medium w-24">Role:</span> 
              <span className="flex-1">{selectedCase.role}</span>
            </p>
            {selectedCase.profile && (
              <>
                <p className="flex items-center">
                  <span className="font-medium w-24">Character:</span> 
                  <span className="flex-1">{selectedCase.profile.name}</span>
                </p>
                <p className="flex items-center">
                  <span className="font-medium w-24">Gender:</span> 
                  <span className="flex-1">{selectedCase.profile.gender}</span>
                </p>
              </>
            )}
          </div>
        </div>
      )}

      <AvatarUserVideo />
    </div>
  );
};

export default AvatarChat;
