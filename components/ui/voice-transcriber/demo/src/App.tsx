import { useEffect, useState } from "react";

import { VoiceRecorder } from "../../widget/src/VoiceRecorder";
import {
  defaultAudioRecordConfig,
  loadAudioRecordConfig,
  saveAudioRecordConfig,
  type AudioRecordConfig,
} from "../../widget/src/config";
import "./styles.css";

type Page = "recorder" | "config";

interface ConfigPageProps {
  config: AudioRecordConfig;
  onSave: (config: AudioRecordConfig) => Promise<void>;
  onClose: () => void;
}

function displayKey(code: string): string {
  if (code === "Space") return "Space bar";
  return code.replace(/^(Key|Digit)/, "");
}

function ConfigPage({ config, onSave, onClose }: ConfigPageProps) {
  const [draft, setDraft] = useState(config);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const save = async () => {
    setSaving(true);
    setMessage("");
    try {
      await onSave(draft);
      setMessage("Configuration saved to disk.");
    } catch {
      setMessage("Configuration could not be saved.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="app-shell">
      <section className="panel config-panel" aria-labelledby="config-title">
        <header className="page-header">
          <div>
            <p className="eyebrow">A-Man</p>
            <h1 id="config-title">Configuration</h1>
          </div>
          <button className="secondary-button" type="button" onClick={onClose}>Done</button>
        </header>
        <div className="tabs" role="tablist" aria-label="Configuration sections">
          <button role="tab" aria-selected="true" type="button">Audio Record</button>
        </div>
        <div className="tab-panel" role="tabpanel">
          <div className="setting-row">
            <div>
              <h2>Push to talk</h2>
              <p>Record only while the configured keyboard key is held.</p>
            </div>
            <label className="switch">
              <input
                type="checkbox"
                checked={draft.push_to_talk_enabled}
                onChange={(event) => setDraft({
                  ...draft,
                  push_to_talk_enabled: event.target.checked,
                })}
              />
              <span aria-hidden="true" />
              <span className="sr-only">Enable push to talk</span>
            </label>
          </div>
          <div className="key-setting">
            <label htmlFor="push-to-talk-key">Push-to-talk button</label>
            <input
              id="push-to-talk-key"
              value={displayKey(draft.push_to_talk_key)}
              readOnly
              disabled={!draft.push_to_talk_enabled}
              onKeyDown={(event) => {
                event.preventDefault();
                setDraft({ ...draft, push_to_talk_key: event.code });
              }}
              aria-describedby="key-help"
            />
            <p id="key-help">Focus this field, then press the key you want to use.</p>
          </div>
          <footer className="config-footer">
            <p role="status">{message}</p>
            <button className="primary-button" type="button" onClick={() => void save()} disabled={saving}>
              {saving ? "Saving…" : "Save configuration"}
            </button>
          </footer>
        </div>
      </section>
    </main>
  );
}

export function App() {
  const [page, setPage] = useState<Page>("recorder");
  const [config, setConfig] = useState(defaultAudioRecordConfig);
  const [configWarning, setConfigWarning] = useState("");
  const [recordingUrl, setRecordingUrl] = useState<string | null>(null);

  useEffect(() => {
    void loadAudioRecordConfig()
      .then(setConfig)
      .catch(() => setConfigWarning("Using default settings; the configuration service is unavailable."));
  }, []);

  useEffect(() => () => {
    if (recordingUrl) URL.revokeObjectURL(recordingUrl);
  }, [recordingUrl]);

  if (page === "config") {
    return (
      <ConfigPage
        config={config}
        onClose={() => setPage("recorder")}
        onSave={async (nextConfig) => {
          const saved = await saveAudioRecordConfig(nextConfig);
          setConfig(saved);
          setConfigWarning("");
        }}
      />
    );
  }

  return (
    <main className="app-shell">
      <section className="panel">
        <header className="page-header">
          <span className="brand">A-Man</span>
          <button className="secondary-button" type="button" onClick={() => setPage("config")}>
            Config
          </button>
        </header>
        <VoiceRecorder
          config={config}
          onRecordingComplete={(blob) => setRecordingUrl((previous) => {
            if (previous) URL.revokeObjectURL(previous);
            return URL.createObjectURL(blob);
          })}
        />
        {configWarning && <p className="warning" role="alert">{configWarning}</p>}
        {recordingUrl && (
          <section className="recording-result" aria-labelledby="latest-recording">
            <h2 id="latest-recording">Latest recording</h2>
            <audio controls src={recordingUrl}>Your browser does not support audio playback.</audio>
            <a className="secondary-button" href={recordingUrl} download="voice-recording.webm">Download</a>
          </section>
        )}
      </section>
    </main>
  );
}
