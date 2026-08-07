import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";

const defaultConfig = {
  push_to_talk_enabled: false,
  push_to_talk_key: "Space",
};

describe("demo application", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => defaultConfig,
    }));
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:recording"),
      revokeObjectURL: vi.fn(),
    });
  });

  it("renders the voice recorder and opens configuration", async () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Record your voice" })).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Config" }));

    expect(screen.getByRole("heading", { name: "Configuration" })).toBeVisible();
    expect(screen.getByRole("tab", { name: "Audio Record" })).toHaveAttribute(
      "aria-selected",
      "true",
    );
    await waitFor(() => expect(fetch).toHaveBeenCalledWith("/v1/config/audio-record"));
  });

  it("edits and saves push-to-talk settings", async () => {
    render(<App />);
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    fireEvent.click(screen.getByRole("button", { name: "Config" }));
    fireEvent.click(screen.getByRole("checkbox", { name: "Enable push to talk" }));
    fireEvent.keyDown(screen.getByLabelText("Push-to-talk button"), {
      code: "KeyV",
      key: "v",
    });
    fireEvent.click(screen.getByRole("button", { name: "Save configuration" }));

    await waitFor(() => expect(fetch).toHaveBeenLastCalledWith(
      "/v1/config/audio-record",
      expect.objectContaining({
        method: "PUT",
        body: JSON.stringify({
          push_to_talk_enabled: true,
          push_to_talk_key: "KeyV",
        }),
      }),
    ));
    expect(await screen.findByText("Configuration saved to disk.")).toBeVisible();
  });
});
