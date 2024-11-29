"use client";
import React, { useEffect, useState, useRef } from "react";
import * as SpeechSDK from "microsoft-cognitiveservices-speech-sdk";
import { webApp } from "@/utils/api";
import { Case } from "@/types/cases";


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

  constructor(config: AvatarConfig) {
    const speechConfig = SpeechSDK.SpeechConfig.fromSubscription(speechKey, speechRegion);

    speechConfig.speechSynthesisLanguage = "pt-BR";
    speechConfig.speechSynthesisVoiceName = "pt-BR-AntonioNeural";

    this.speechConfig = speechConfig;
    this.avatarConfig = new SpeechSDK.AvatarConfig(config.character, config.style, config.videoFormat);
  }

  public updateLanguage(language: string, voice: string) {
    // Update language and voice for TTS
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
      throw new Error("Failed to fetch ICE server information");
    }

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
      if (event.track.kind === "video" && videoRef.current) {
        const videoElement = document.createElement("video");
        videoElement.id = "videoPlayer";
        videoElement.srcObject = event.streams[0];
        videoElement.autoplay = true;
        videoElement.playsInline = true;
  
        videoRef.current.innerHTML = "";
        videoRef.current.appendChild(videoElement);
      }
    };
  
    await this.avatarSynthesizer.startAvatarAsync(peerConnection);
    console.log("Avatar session started.");
  }

  public async getAvatarResponse(spokenText: string, chatHistory: string, chatId: Case) {
    try {
      const response = await webApp.post("/response", {
        prompt: spokenText,
        chat_history: JSON.stringify(chatHistory),
        case_id: chatId?.id
      });

      if (response.status === 200 || response.status === 201) {
        console.log(response?.data?.text);
        return response?.data?.text;
      } else {
        console.error("Error occurred while creating the job.");
        return null;
      }
    } catch (error) {
      console.error("Error initiating the job:", error);
      return "Error initiating the job.";
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
          const cancellationDetails = SpeechSDK.CancellationDetails.fromResult(result);
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
    // Update STT language
    const audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
    this.speechRecognizer = new SpeechSDK.SpeechRecognizer(this.speechConfig, audioConfig);

    this.speechRecognizer.recognized = (s, e) => {
      if (e.result.reason === SpeechSDK.ResultReason.RecognizedSpeech) {
        console.log("Recognized text:", e.result.text);
        onRecognized(e.result.text);
      }
    };

    // Set the recognition language
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
  const audioRef = useRef<HTMLDivElement>(null);
  const [spokenText, setSpokenText] = useState("");
  const avatarHandlerRef = useRef<AvatarHandler | null>(null);
  const [isMicrophoneActive, setIsMicrophoneActive] = useState(false);
  const [isChatHistory, setChatHistory] = useState<object[] | null>(null);
  const [isChatId, setChatId] = useState<Case | null>(null);

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const response = await webApp.get("/profile");
        if (response.status === 200) {
          setChatId(response?.data?.result);
  
          const gender = response?.data?.result?.profile?.gender || "male";
          const language = "pt-BR";
          const voice = gender === "feminino" ? "pt-BR-FranciscaNeural" : "pt-BR-AntonioNeural";
  
          avatarHandlerRef.current = new AvatarHandler({
            character: gender === "feminino" ? "lisa" : "harry",
            style: gender === "feminino" ? "casual-sitting" : "casual",
            videoFormat: new SpeechSDK.AvatarVideoFormat("H264", 2000000, 1920, 1080),
          });
  
          avatarHandlerRef.current.speechConfig.speechSynthesisLanguage = language;
          avatarHandlerRef.current.speechConfig.speechSynthesisVoiceName = voice;
  
          console.log(`Configured TTS language to ${language} and voice to ${voice}`);
        }
      } catch (error) {
        console.error("Error fetching profile data:", error);
      }
    };
  
    fetchProfileData();
  }, []);

  const handleStartAvatar = async () => {
    console.log(isChatId?.profile?.gender);
    if (avatarHandlerRef.current && videoRef.current) {
      setIsLoading(true);
      try {
        await avatarHandlerRef.current.startAvatar(videoRef);
        console.log("Avatar session started.");
      } catch (error) {
        console.error("Failed to start avatar:", error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleChat = async () => {
    if (avatarHandlerRef.current && spokenText) {
      try {
        if (!isChatHistory) {
          const newChatHistory = [{ user: spokenText }];
          setChatHistory(newChatHistory);
        } else {
          const updatedChatHistory = [...isChatHistory, { user: spokenText }];
          setChatHistory(updatedChatHistory);
        }

        const response = await avatarHandlerRef.current.getAvatarResponse(spokenText, isChatHistory ? isChatHistory.toString() : "", isChatId);

        if (response) {
          setChatHistory((prev) => [...(prev || []), { assistant: response }]);
        }
        avatarHandlerRef.current.chat(response);
        console.log("Message sent to avatar:", response);
      } catch (error) {
        console.error("Failed to send message to avatar:", error);
      }
    }
  };

  const handleStopAvatar = () => {
    if (avatarHandlerRef.current) {
      avatarHandlerRef.current.stopAvatar();
      console.log("Avatar session stopped.");
    }
  };

  const toggleMicrophone = () => {
    if (avatarHandlerRef.current) {
      if (isMicrophoneActive) {
        avatarHandlerRef.current.stopMicrophone();
      } else {
        avatarHandlerRef.current.startMicrophone((text) => setSpokenText((prev) => `${prev} ${text}`));
      }
      setIsMicrophoneActive(!isMicrophoneActive);
    }
  };

  return (
    <>
    <div>
      {isChatId ? (
        <div className="bg-gray-100 p-4 rounded shadow-md mb-4">
          <p className="text-gray-700"><strong>Nome:</strong> {isChatId?.profile?.name}</p>
          <p className="text-gray-700"><strong>Gênero:</strong> {isChatId?.profile?.gender}</p>
          <p className="text-gray-700"><strong>Profissão:</strong> {isChatId?.profile?.role}</p>
        </div>
      ) : (
        <p className="text-gray-700">Nenhum caso carregado.</p>
      )}
    </div>
    <div className="flex flex-row items-start w-full px-8 gap-8">
      <div className="flex flex-col items-center w-2/3">
        <div ref={videoRef} className="w-full h-full rounded my-6"></div>
        <div ref={audioRef} className="hidden"></div>
        <div className="flex justify-evenly w-full">
          <button
            onClick={handleStartAvatar}
            disabled={isLoading}
            className={`px-4 py-2 ${
              isLoading ? "bg-primary" : "bg-kelly-green hover:bg-non-photo-blue text-white"
            } rounded`}
          >
            {isLoading ? "Starting..." : "Start Avatar"}
          </button>
          <button
            onClick={handleStopAvatar}
            className="bg-fulvous hover:bg-puce text-white px-4 py-2 rounded"
          >
            Stop Avatar
          </button>
        </div>
      </div>
      <div className="flex flex-col items-start w-1/3">
        {/* Chat Messages */}
        <div className="flex flex-col w-full bg-gray-100 p-4 rounded shadow-md mb-4 h-[60vh] overflow-y-auto">
          {isChatHistory && isChatHistory.length > 0 ? (
            isChatHistory.map((message, index) => (
              <div key={index} className="mb-2">
                {Object.entries(message).map(([key, value]) => (
                  <p key={key} className="text-gray-700">
                    <strong>{key === "assistant" ? "paciente": "você"}:</strong> {value}
                  </p>
                ))}
              </div>
            ))
          ) : (
            <p className="text-gray-700">Chat messages will appear here...</p>
          )}
        </div>

        {/* Chat Input */}
        <textarea
          value={spokenText}
          onChange={(e) => setSpokenText(e.target.value)}
          placeholder="Type your message here..."
          className="w-full p-2 border rounded mb-4"
        />
        <div className="flex justify-between w-full">
          <button
            onClick={handleChat}
            className="bg-non-photo-blue hover:kelly-green text-white px-4 py-2 flex-1 mr-2 rounded"
            disabled={!spokenText}
          >
            Send to Avatar
          </button>

          <button
            onClick={toggleMicrophone}
            className={`px-4 py-2 flex items-center justify-center ${
              isMicrophoneActive ? "bg-fulvous" : "bg-non-photo-blue hover:kelly-green"
            } rounded`}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d={
                  isMicrophoneActive
                    ? "M12 1v11M12 20v2M5 15h14M5 9a7 7 0 0 1 14 0"
                    : "M12 5v6m7 4v2m-7 3v2m-7-3v2m14-8H5"
                }
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
    </>
  );
};

export default AvatarChat;
