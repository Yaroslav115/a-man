export interface AudioRecordConfig {
  push_to_talk_enabled: boolean;
  push_to_talk_key: string;
}

export const defaultAudioRecordConfig: AudioRecordConfig = {
  push_to_talk_enabled: false,
  push_to_talk_key: "Space",
};

export async function loadAudioRecordConfig(
  fetcher: typeof fetch = fetch,
): Promise<AudioRecordConfig> {
  const response = await fetcher("/v1/config/audio-record");
  if (!response.ok) throw new Error("Could not load audio recorder configuration");
  return response.json() as Promise<AudioRecordConfig>;
}

export async function saveAudioRecordConfig(
  config: AudioRecordConfig,
  fetcher: typeof fetch = fetch,
): Promise<AudioRecordConfig> {
  const response = await fetcher("/v1/config/audio-record", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  if (!response.ok) throw new Error("Could not save audio recorder configuration");
  return response.json() as Promise<AudioRecordConfig>;
}
