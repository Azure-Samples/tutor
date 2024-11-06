import * as SpeechSDK from "microsoft-cognitiveservices-speech-sdk";


type AvatarConfig = {
    character: string;
    style: string;
    videoFormat: SpeechSDK.AvatarVideoFormat;
}


class AvatarEngine {
    private audioConfig: SpeechSDK.AudioConfig;
    private speechConfig: SpeechSDK.SpeechConfig;
    private avatarConfig: SpeechSDK.AvatarConfig;

    constructor(config: AvatarConfig) {
        this.audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
        this.speechConfig = SpeechSDK.SpeechConfig.fromSubscription("YourSpeechKey", "YourSpeechRegion");
        this.avatarConfig = new SpeechSDK.AvatarConfig(
            config.character,
            config.style,
            config.videoFormat
        );
    }

    public async startAvatar() {
        const synthesizer = new SpeechSDK.SpeechSynthesizer(this.speechConfig, this.audioConfig);
        const avatar = new SpeechSDK.Avatar(synthesizer, this.avatarConfig);
        await avatar.startSpeakingAsync("Hello, World!");
    }
}


const speechConfig = SpeechSDK.SpeechConfig.fromSubscription("YourSpeechKey", "YourSpeechRegion");
const videoFormat = new SpeechSDK.AvatarVideoFormat("H264", 2000000, 1920, 1080);

speechConfig.speechSynthesisLanguage = "pt-BR";
speechConfig.speechSynthesisVoiceName = "en-US-AvaMultilingualNeural";   

const avatarConfig = new SpeechSDK.AvatarConfig(
    "lisa", // Set avatar character here.
    "casual-sitting", // Set avatar style here.
    videoFormat // Set video format here.
);


let peerConnection = new RTCPeerConnection(
    {
        iceServers: [
            {
                urls: [ "" ],
                username: "",
                credential: ""
            }
        ]
    }
)

peerConnection.ontrack = function (event) {
    if (event.track.kind === 'video') {
        const videoElement = document.createElement(event.track.kind)
        videoElement.id = 'videoPlayer'
        videoElement.srcObject = event.streams[0]
        videoElement.autoplay = true
    }

    if (event.track.kind === 'audio') {
        const audioElement = document.createElement(event.track.kind)
        audioElement.id = 'audioPlayer'
        audioElement.srcObject = event.streams[0]
        audioElement.autoplay = true
    }
}

peerConnection.addTransceiver('video', { direction: 'sendrecv' })
peerConnection.addTransceiver('audio', { direction: 'sendrecv' })