import * as SpeechSDK from "microsoft-cognitiveservices-speech-sdk";
import * as dotenv from 'dotenv';

dotenv.config();


const speechKey = process.env.SPEECH_KEY;
const speechRegion = process.env.SPEECH_REGION;


type AvatarConfig = {
    character: string;
    style: string;
    videoFormat: SpeechSDK.AvatarVideoFormat;
}


interface AvatarHandler<Request = string, Result = string> {

    setNext(handler: AvatarHandler<Request, Result>): AvatarHandler<Request, Result>;
    readModel(request: Request): Result;
    startAvatar(): void;
    chat(spokenText: string): Promise<void>;

}


abstract class AbstractAvatarHandler implements AvatarHandler {

    private nextHandler: AvatarHandler | null = null;
    private speechConfig: SpeechSDK.SpeechConfig;
    private avatarConfig: SpeechSDK.AvatarConfig;
    private peerConnection!: RTCPeerConnection;

    constructor(config: AvatarConfig) {
        this.speechConfig = SpeechSDK.SpeechConfig.fromSubscription(speechKey, speechRegion);
        this.avatarConfig = new SpeechSDK.AvatarConfig(
            config.character,
            config.style,
            config.videoFormat
        );
    }

    private _avatar(): SpeechSDK.AvatarSynthesizer {
        return new SpeechSDK.AvatarSynthesizer(this.speechConfig, this.avatarConfig);
    }

    private async fetchIceServers(): Promise<RTCIceServer[]> {
        const response = await fetch(`https://${speechRegion}.tts.speech.microsoft.com/cognitiveservices/avatar/relay/token/v1`, {
            method: 'GET',
            headers: {
                'Ocp-Apim-Subscription-Key': speechKey
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch ICE server information');
        }

        const data = await response.json();
        return data.iceServers;
    }

    private async initializePeerConnection() {
        try {
            const iceServers = await this.fetchIceServers();
            this.peerConnection = new RTCPeerConnection({ iceServers });
            this.peerConnection.addTransceiver('video', { direction: 'sendrecv' })
            this.peerConnection.addTransceiver('audio', { direction: 'sendrecv' })
        } catch (error) {
            console.error('Error initializing peer connection:', error);
        }
    }

    public setNext(handler: AvatarHandler): AvatarHandler {
        this.nextHandler = handler;
        return handler;
    }

    public readModel(request: string): string {
        if (this.nextHandler) {
            return this.nextHandler.readModel(request);
        }
        return "";
    }

    public async startAvatar() {
        this.initializePeerConnection();
        this._avatar().startAvatarAsync(this.peerConnection).then(
            (r: SpeechSDK.SpeechSynthesisResult) => { console.log("Avatar started.", r) }
        ).catch(
            (error: any) => { console.log("Avatar failed to start. Error: " + error) }
        );
    }

    public async chat(spokenText: string): Promise<void> {
        const avatar = this._avatar();
        this.startAvatar();
        await avatar.speakTextAsync(spokenText).then(
            (result: SpeechSDK.SpeechSynthesisResult) => {
            if (result.reason === SpeechSDK.ResultReason.SynthesizingAudioCompleted) {
                console.log("Speech and avatar synthesized to video stream.")
            } else {
                console.log("Unable to speak. Result ID: " + result.resultId)
                if (result.reason === SpeechSDK.ResultReason.Canceled) {
                let cancellationDetails: SpeechSDK.CancellationDetails = SpeechSDK.CancellationDetails.fromResult(result)
                console.log(cancellationDetails.reason)
                if (cancellationDetails.reason === SpeechSDK.CancellationReason.Error) {
                    console.log(cancellationDetails.errorDetails)
                }
                }
            }
        }).catch((error: any) => {
            console.log(error)
            avatar.close()
        });
    }

}


class TeachHandler extends AbstractAvatarHandler {
    public readModel(request: string): string {
        if (request === 'Banana') {
            return `Monkey: I'll eat the ${request}.`;
        }
        return super.readModel(request);

    }
}


class EvaluateHandler extends AbstractAvatarHandler {
    public readModel(request: string): string {
        if (request === 'Nut') {
            return `Squirrel: I'll eat the ${request}.`;
        }
        return super.readModel(request);
    }
}


class SuggestHandler extends AbstractAvatarHandler {
    public readModel(request: string): string {
        if (request === 'MeatBall') {
            return `Dog: I'll eat the ${request}.`;
        }
        return super.readModel(request);
    }
}


function clientCode(handler: AvatarHandler) {
    const foods = ['Nut', 'Banana', 'Cup of coffee'];

    for (const food of foods) {
        console.log(`Client: Who wants a ${food}?`);

        const result = handler.readModel(food);
        if (result) {
            console.log(`  ${result}`);
        } else {
            console.log(`  ${food} was left untouched.`);
        }
    }
}


const monkey = new TeachHandler();
const squirrel = new EvaluateHandler();
const dog = new SuggestHandler();

monkey.setNext(squirrel).setNext(dog);

/**
 * The client should be able to send a request to any handler, not just the
 * first one in the chain.
 */
console.log('Chain: Monkey > Squirrel > Dog\n');
clientCode(monkey);
console.log('');

console.log('Subchain: Squirrel > Dog\n');
clientCode(squirrel);