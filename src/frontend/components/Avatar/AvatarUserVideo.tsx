import React, { useEffect, useRef, useState } from "react";
import { FaVideo, FaVideoSlash } from "react-icons/fa";

const AvatarUserVideo: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [stream, setStream] = useState<MediaStream | null>(null);

  useEffect(() => {
    if (isVideoOn) {
      navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        .then(mediaStream => {
          setStream(mediaStream);
          if (videoRef.current) {
            videoRef.current.srcObject = mediaStream;
          }
        })
        .catch((err) => {
          console.error("Error accessing camera:", err);
        });
    } else if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [isVideoOn]);

  const toggleVideo = () => {
    setIsVideoOn(prev => !prev);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 bg-white dark:bg-boxdark rounded-xl shadow-lg p-2 flex items-center gap-3">
      <button 
        onClick={toggleVideo}
        className={`rounded-full p-2 ${isVideoOn ? 'bg-cyan-600 text-white' : 'bg-gray-300 text-gray-600'}`}
      >
        {isVideoOn ? <FaVideo /> : <FaVideoSlash />}
      </button>
      {isVideoOn ? (
        <video ref={videoRef} autoPlay muted playsInline className="w-32 h-24 rounded-lg object-cover" />
      ) : (
        <div className="w-32 h-24 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
          <span className="text-xs text-gray-500 dark:text-gray-400">Camera off</span>
        </div>
      )}
    </div>
  );
};

export default AvatarUserVideo;
