interface PyWebViewAPI {
	toggleFullscreen: () => Promise<Any>;
	start: (runs: number) => Promise<Any>;
	status: () => Promise<Any>;
	pause: () => Promise<Any>;
	stop: () => Promise<Any>;
	get_logs: () => Promise<Any>;
	get_inventory: () => Promise<Any>;
	get_cycles: () => Promise<Any>;
	get_emulators: () => Promise<Any>;
	connect_emulator: (port: string) => Promise<Any>;
	set_emulator_port: (port: string) => Promise<Any>;
	kill_adb: () => Promise<Any>;
	restart_adb: () => Promise<Any>;
	toggleCeciliaBot: () => Promise<Any>;
}

interface PyWebView {
	api: PyWebViewAPI;
}

declare global {
	interface Window {
		pywebview: PyWebView;
	}
}

export { };
