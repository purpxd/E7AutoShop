import { useEffect, useState, useRef } from 'react'
import './App.css'
import lobby from './assets/l.gif'
import arky from './assets/a.png'
import arkyicon from './assets/a.ico'
import { Inventory } from './components/Inventory'
import { Footer } from './components/Footer'
import { Timer } from './components/Timer'
import { Logs } from './components/Logs'
import { Toaster, toast } from 'sonner'
import { ChevronDown } from 'lucide-react'
import { SettingsComponent } from './components/Settings'
import { X } from 'lucide-react'
import { ResourceType, Resources, Log } from './types/utils.d'
function App() {
  const [running, setRunning] = useState<boolean>(false);
  const [paused, setPaused] = useState<boolean>(false);
  const [skystones, setSkystones] = useState<number | null>(null);
  const [cycles, setCycles] = useState<number>(0);
  const [command, setCommand] = useState<string>('');
  const [inventory, setInventory] = useState<Resources>({ 'g': 0, 'b': 0, 'm': 0, 's': 0 });
  const [logs, setLogs] = useState<Log[]>([]);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  let interval: number;


  async function pollAPI() {
    const status = await window.pywebview.api.status()
    const data = await window.pywebview.api.get_logs()
    const i = await window.pywebview.api.get_inventory()
    const c = await window.pywebview.api.get_cycles()
    setCycles(c)
    const bag: Resources = {
      [ResourceType.Bookmarks]: i.b,
      [ResourceType.Gold]: i.g,
      [ResourceType.Mystics]: i.m,
      [ResourceType.Skystones]: i.s,

    }
    setInventory(bag)
    setLogs(data)
    if (status != true) {
      await stop();
    }
  }

  async function sendPort (port: string) {
    try {
      await window.pywebview.api.set_emulator_port(port)
    } catch (e) {
    }
  };

  useEffect(() => {
    toast("Welcome to E7 Autoshop", {icon: <img src={arkyicon} />,  description: 'If the tool has been useful to you, please ⭐ the project on GitHub and donate on Ko-fi 😀', duration: 5000})
  }, [])

  useEffect(() => {
    const ePort = localStorage.getItem('emulatorPort')
    if (ePort != undefined) {
        setTimeout(() => {
        sendPort(ePort);
        }, 1000)
    }
  }, [])

  useEffect(() => {
    if (scrollContainerRef.current) {
      if (!paused) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
      }
    }
  }, [logs, paused]);

  function determinePercentage() {
    const totalIterations = Math.floor(skystones! / 3);
    const percentage = Math.floor((cycles / totalIterations) * 100);
    if (Number.isFinite(percentage)) {
      return percentage
    } else {
      return 0
    }
  }

  async function startRun() {
    setCommand("start")
    setCycles(0)
    toast('Starting');
    window.pywebview.api.start(Math.floor(skystones! / 3))
    interval = setInterval(pollAPI, 1000)
  }

  async function pause() {
    setCommand("paused")
    toast('Pausing');
    setPaused(!paused)
    if (paused) {
      clearInterval(interval);
    } else {
      interval = setInterval(pollAPI, 1000)
    }
    window.pywebview.api.pause()
  }

  async function stop() {
    setCommand("stop")
    setPaused(false)
    setRunning(false)
    toast('Finished');
    window.pywebview.api.stop()
    clearInterval(interval);
  }

  const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    if (inputValue === '' || /^[0-9]+$/.test(inputValue)) {
      setSkystones(Number(inputValue));
    }
  };
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <>
      <Toaster position="top-right" />
      <div className='mx-auto flex flex-col items-center gap-1'>
        <div className='flex flex-row w-full justify-between items-center'>
          <div className='flex flex-row items-center mb-2'>
            <img src={arky} className='h-10 w-12' alt="" />
            <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-purple-800 bg-clip-text text-transparent">
              E7 AutoShop
            </h1>
          </div>

          <div className='flex flex-row gap-1 border rounded-lg border-slate-600'>
            <button className='btn'>Emulator</button>
            <button className='btn' disabled={true}>Client</button>
          </div>
        </div>
        <img src={lobby} alt="" />
        <div className='w-full flex flex-row items-center gap-2'>
          <progress className="progress progress-primary w-full" value={determinePercentage()} max="100"></progress>
          <span>{isNaN(determinePercentage()) ? 0 : determinePercentage()}%</span>
        </div>
        <div className="w-full flex justify-center">
          <Inventory inventory={inventory} />
        </div>

        <div className='flex flex-row gap-2 mt-5 w-full gap-3 items-center'>
          <Timer isRunning={running} isPaused={paused} command={command} />
          <div className='relative w-full'>
            <input type="text"
              placeholder="Enter skystone amount"
              className="input w-full"
              value={skystones!}
              onChange={handleInput}
              disabled={running} />
            <div className='absolute top-2 right-2'>
              {skystones! > 0 && (
                <X size={20} style={{ opacity: 0.6 }} onClick={() => {
                  if (!running) {
                    setSkystones(0)
                  }
                }} />
              )}
            </div>
          </div>
          {!running ? (
            <button
              className="btn"
              disabled={skystones === null || skystones < 3}
              onClick={async () => {
                setRunning(!running);
                startRun()
              }
              }>Start</button>
          ) : (
            <>
              <button className="btn" onClick={() => pause()}>
                {!paused ? 'Pause' : 'Resume'}
              </button>
              <button className="btn" onClick={() => { setRunning(!running); stop() }}>Stop</button>
            </>
          )
          }
        </div>
        <div className="text-center w-full relative">
          <button
            className="btn-wide max-h-8 flex justify-center items-center mx-auto my-2"
            onClick={toggleCollapse}
            aria-expanded={isCollapsed}
            data-toggle="collapse"
            data-target="#collapseButton"
            aria-controls="collapseButton"
          >
            <ChevronDown className={`transition-transform ${isCollapsed ? "rotate-180" : ""}`} />
          </button>
          <div className="overflow-hidden transition-[max-height] duration-300 ease-in-out max-h-0 m-5" id="collapseButton">
            <div className="overflow-y-auto bg-slate border border-slate-200 rounded-lg shadow-sm p-4 z-10 w-[500px] h-[200px] mx-auto"
            ref={scrollContainerRef}
            >
              <Logs logs={logs} />
            </div>
          </div>
          <SettingsComponent />
        </div>
        <Footer />
      </div >
    </>
  )
}

export default App
