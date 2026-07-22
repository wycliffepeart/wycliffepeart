"use client";

import { useResumeModal } from "./resume-modal-context";

export default function ResumeOpenButton() {
  const { open } = useResumeModal();

  return (
    <button className="button primary" type="button" onClick={open}>
      Resume
    </button>
  );
}
