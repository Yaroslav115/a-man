import { useCallback, useEffect, useRef, useState } from "react";

import type { AudioRecordConfig } from "./config";

interface VoiceRecorderProps {
  config: AudioRecordConfig;
  onRecordingComplete?: (recording: Blob) => void;
}

function isEditableTarget(target: EventTarget | null): boolean {
  return target instanceof HTMLElement &&
    (target.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName));
}

export function VoiceRecorder({ config, onRecordingComplete }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const start = useCallback(async () => {
    if (recorderRef.current || isRecording) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      streamRef.current = stream;
      recorderRef.current = recorder;
      chunksRef.current = [];
      recorder.ondataavailable = ({ data }) => {
        if (data.size) chunksRef.current.push(data);
      };
      recorder.onstop = () => {
        const recording = new Blob(chunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        });
        stream.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
        recorderRef.current = null;
        setIsRecording(false);
        if (recording.size) onRecordingComplete?.(recording);
      };
      recorder.start();
      setError(null);
      setIsRecording(true);
    } catch {
      setError("Microphone access was denied or is unavailable.");
    }
  }, [isRecording, onRecordingComplete]);

  const stop = useCallback(() => {
    if (recorderRef.current?.state === "recording") recorderRef.current.stop();
  }, []);

  useEffect(() => {
    if (!config.push_to_talk_enabled) return;
    const keyDown = (event: KeyboardEvent) => {
      if (event.code !== config.push_to_talk_key || event.repeat || isEditableTarget(event.target)) return;
      event.preventDefault();
      void start();
    };
    const keyUp = (event: KeyboardEvent) => {
      if (event.code !== config.push_to_talk_key) return;
      event.preventDefault();
      stop();
    };
    window.addEventListener("keydown", keyDown);
    window.addEventListener("keyup", keyUp);
    return () => {
      window.removeEventListener("keydown", keyDown);
      window.removeEventListener("keyup", keyUp);
    };
  }, [config, start, stop]);

  useEffect(() => () => {
    if (recorderRef.current?.state === "recording") recorderRef.current.stop();
    streamRef.current?.getTracks().forEach((track) => track.stop());
  }, []);

  return (
    <section className="recorder" aria-labelledby="recorder-title">
      <p className="eyebrow">Audio recorder</p>
      <h1 id="recorder-title">Record your voice</h1>
      <p className="summary">
        {config.push_to_talk_enabled
          ? `Hold ${config.push_to_talk_key} to record.`
          : "Press the microphone button to start and stop recording."}
      </p>
      <button
        className={`record-button${isRecording ? " recording" : ""}`}
        type="button"
        aria-pressed={isRecording}
        onClick={() => (isRecording ? stop() : void start())}
      >
        <span aria-hidden="true">{isRecording ? "■" : "●"}</span>
        {isRecording ? "Stop recording" : "Start recording"}
      </button>
      <p className="record-status" role="status">
        {error ?? (isRecording ? "Recording…" : "Ready")}
      </p>
    </section>
  );
}
