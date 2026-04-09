import type React from "react";
import { useEffect, useRef } from "react";

interface Props {
  children: React.ReactNode;
  exceptionRef?: React.RefObject<HTMLElement>;
  onClick: () => void;
  className?: string;
}

const ClickOutside: React.FC<Props> = ({ children, exceptionRef, onClick, className }) => {
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickListener = (event: MouseEvent) => {
      const targetNode = event.target as Node;
      const clickedInsideWrapper = wrapperRef.current?.contains(targetNode) ?? false;
      const clickedInsideException =
        (exceptionRef?.current !== null && exceptionRef?.current === targetNode) ||
        (exceptionRef?.current?.contains(targetNode) ?? false);
      const clickedInside = clickedInsideWrapper || clickedInsideException;

      if (!clickedInside) onClick();
    };

    document.addEventListener("mousedown", handleClickListener);

    return () => {
      document.removeEventListener("mousedown", handleClickListener);
    };
  }, [exceptionRef, onClick]);

  return (
    <div ref={wrapperRef} className={`${className || ""}`}>
      {children}
    </div>
  );
};

export default ClickOutside;
