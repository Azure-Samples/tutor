"use client";

import { useRef, useEffect } from "react";

// FormsModal with header, rounded close button, and default Submit/Cancel buttons
const FormsModal = ({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}) => {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handleClickOutside = (event: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
        onClose();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-10 flex items-center justify-center bg-black bg-opacity-40 w-screen">
      <div
        ref={modalRef}
        className="bg-white dark:bg-boxdark rounded-3xl shadow-2xl w-full max-w-4xl md:max-w-4xl lg:max-w-4xl xl:max-w-4xl 2xl:max-w-4xl relative flex flex-col max-h-[80vh] h-auto"
      >
        <div className="sticky top-0 z-20 flex items-center justify-between px-6 py-4 border-b border-cyan-100 dark:border-cyan-900 rounded-t-3xl bg-gradient-to-r from-cyan-100 via-blue-50 to-green-100 dark:from-cyan-900 dark:via-blue-950 dark:to-green-900">
          <h2 className="text-xl font-bold text-cyan-700 dark:text-cyan-200 flex-1">{title}</h2>
          <button
            className="ml-4 w-10 h-10 flex items-center justify-center rounded-full bg-cyan-200 dark:bg-cyan-800 text-cyan-700 dark:text-cyan-100 hover:bg-cyan-300 hover:scale-110 transition-all text-2xl shadow"
            onClick={onClose}
            aria-label="Close modal"
          >
            ×
          </button>
        </div>
        <div className="flex-1 flex flex-col justify-between px-6 py-6 h-full overflow-y-auto">
          <div className="flex-1 flex flex-col justify-center">
            {children}
          </div>
        </div>
        <div className="sticky bottom-0 z-20 flex gap-4 justify-end px-6 py-6 bg-white dark:bg-boxdark rounded-b-3xl border-t border-cyan-100 dark:border-cyan-900">
          <button
            className="px-6 py-3 rounded-2xl bg-gradient-to-br from-green-400 to-cyan-400 hover:from-cyan-400 hover:to-yellow-300 text-white font-bold shadow-lg transition-all duration-200"
            type="submit"
            form="modal-form"
          >
            Submit
          </button>
          <button
            className="px-6 py-3 rounded-2xl bg-gray-200 dark:bg-gray-700 text-cyan-700 dark:text-cyan-100 font-bold shadow hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-200"
            type="button"
            onClick={onClose}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default FormsModal;