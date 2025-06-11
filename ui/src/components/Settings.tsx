import { useState } from "react"
import { Settings } from "lucide-react";
import { useEffect } from "react";

export function SettingsComponent() {
  const [visible, setVisible] = useState<boolean>(false);
  const [port, setPort] = useState<string>("5554")

  useEffect(() => {
    const sendPort = async () => {
      try {
        await window.pywebview.api.set_emulator_port(port)
      } catch (e) {
      }
    };
    sendPort();
    const ePort = localStorage.getItem('emulatorPort')
    if (ePort != undefined) {
      setPort(ePort);
    }
  }, [])

  async function saveEmulatorPort(port: string) {
    setPort(port)
    localStorage.setItem('emulatorPort', port)
    await window.pywebview.api.set_emulator_port(port)
  }

  return (
    <>
      <button className="btn btn-sm absolute right-25 top-1.5 " onClick={() => setVisible(!visible)}>
        <Settings size={20} />
      </button>
      <dialog className={`modal ${visible ? 'modal-open' : 'modal-close'}`}>
        <div className="modal-box">
            <div className="flex flex-col gap-2 border rounded-lg p-2">
            <label className="justify start">ADB</label>
            <div className="flex flex-row gap-2 items-center">
            <label className="input">
              <span className="label">emulator</span>
                {port && (
                  <input
                    type="text"
                    value={port}
                    onChange={(event) => {
                      setPort(event.target.value);
                      console.log(event.target.value)
                    }}
                    placeholder="port"
                  />
                )}
            </label>
            <button className="btn btn-sm" onClick={() => {saveEmulatorPort(port)}}>Save</button>
            </div>
            <div className="flex flex-row gap-2">
              <button className="btn" onClick={() => { window.pywebview.api.restart_adb() }}>Restart</button>
              <button className="btn" onClick={() => { window.pywebview.api.connect_emulator(port) }}>Connect</button>
            </div>
          </div>
        </div>
        <form method="dialog" className="modal-backdrop" style={{ opacity: 0.1 }}>
          <button onClick={() => setVisible(!visible)}>close</button>
        </form>
      </dialog>
    </>
  )
}
