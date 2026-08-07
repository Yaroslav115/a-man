import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { VoiceRecorder } from "../../widget/src/VoiceRecorder";

class FakeMediaRecorder {
  static instances: FakeMediaRecorder[] = [];
  state: RecordingState = "inactive";
  mimeType = "audio/webm";
  ondataavailable: ((event: BlobEvent) => void) | null = null;
  onstop: (() => void) | null = null;

  constructor(public stream: MediaStream) {
    FakeMediaRecorder.instances.push(this);
  }

  start() { this.state = "recording"; }
  stop() {
    this.ondataavailable?.({ data: new Blob(["voice"]) } as BlobEvent);
    this.state = "inactive";
    this.onstop?.();
  }
}

describe("VoiceRecorder", () => {
  const stopTrack = vi.fn();

  beforeEach(() => {
    FakeMediaRecorder.instances = [];
    stopTrack.mockClear();
    vi.stubGlobal("MediaRecorder", FakeMediaRecorder);
    Object.defineProperty(navigator, "mediaDevices", {
      configurable: true,
      value: {
        getUserMedia: vi.fn().mockResolvedValue({
          getTracks: () => [{ stop: stopTrack }],
        }),
      },
    });
  });

  it("records from the microphone and returns an audio blob", async () => {
    const onComplete = vi.fn();
    render(
      <VoiceRecorder
        config={{ push_to_talk_enabled: false, push_to_talk_key: "Space" }}
        onRecordingComplete={onComplete}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Start recording" }));
    await screen.findByRole("button", { name: "Stop recording" });
    fireEvent.click(screen.getByRole("button", { name: "Stop recording" }));

    await waitFor(() => expect(onComplete).toHaveBeenCalledOnce());
    expect(onComplete.mock.calls[0][0]).toBeInstanceOf(Blob);
    expect(stopTrack).toHaveBeenCalledOnce();
  });

  it("starts and stops using the configured push-to-talk key", async () => {
    render(
      <VoiceRecorder config={{ push_to_talk_enabled: true, push_to_talk_key: "KeyV" }} />,
    );

    fireEvent.keyDown(window, { code: "KeyV" });
    await screen.findByText("Recording…");
    fireEvent.keyUp(window, { code: "KeyV" });

    await screen.findByText("Ready");
    expect(FakeMediaRecorder.instances).toHaveLength(1);
  });
});
