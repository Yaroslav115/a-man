import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "./App";

describe("demo application", () => {
  it("renders the base frontend", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", { name: "Voice Transcriber Demo" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Frontend ready")).toBeVisible();
  });
});
