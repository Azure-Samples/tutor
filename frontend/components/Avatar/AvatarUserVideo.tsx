import type React from "react";
import { useEffect, useRef, useState } from "react";
import { FaVideo, FaVideoSlash } from "react-icons/fa";

const stopStreamTracks = (mediaStream: MediaStream | null) => {
  if (!mediaStream) {
    return;
  }

  for (const track of mediaStream.getTracks()) {
    track.stop();
  }
};

const AvatarUserVideo: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [stream, setStream] = useState<MediaStream | null>(null);

  useEffect(() => {
    let activeStream: MediaStream | null = null;
    let isCancelled = false;
    const videoElement = videoRef.current;

    if (isVideoOn) {
      navigator.mediaDevices
        .getUserMedia({ video: true, audio: false })
        .then((mediaStream) => {
          if (isCancelled) {
            stopStreamTracks(mediaStream);
            return;
          }

          activeStream = mediaStream;
          setStream(mediaStream);
          if (videoElement) {
            videoElement.srcObject = mediaStream;
          }
        })
        .catch((err) => {
          console.error("Error accessing camera:", err);
        });
    } else {
      setStream((currentStream) => {
        stopStreamTracks(currentStream);
        return null;
      });
      if (videoElement) {
        videoElement.srcObject = null;
      }
    }

    return () => {
      isCancelled = true;
      stopStreamTracks(activeStream);
      if (!isVideoOn && videoElement) {
        videoElement.srcObject = null;
      }
    };
  }, [isVideoOn]);

  const toggleVideo = () => {
    setIsVideoOn((prev) => !prev);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-xl bg-white p-2 shadow-lg dark:bg-boxdark">
      <button
        type="button"
        onClick={toggleVideo}
        className={`rounded-full p-2 ${isVideoOn ? "bg-cyan-600 text-white" : "bg-gray-300 text-gray-600"}`}
      >
        {isVideoOn ? <FaVideo /> : <FaVideoSlash />}
      </button>
      {isVideoOn ? (
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          className="h-24 w-32 rounded-lg object-cover"
        />
      ) : (
        <div className="flex h-24 w-32 items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-700">
          <span className="text-xs text-gray-500 dark:text-gray-400">Camera off</span>
        </div>
      )}
    </div>
  );
};

export default AvatarUserVideo;
