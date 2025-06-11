import arky from '../assets/a.png'
import { Heart, Book } from 'lucide-react'
export function Footer() {
  return (
    <footer className="footer sm:footer-horizontal bg-neutral text-neutral-content items-center p-4">
      <aside className="grid-flow-col items-center">
        <img src={arky} className='h-6 w-8' alt="" />
        <p>E7AutoShop {new Date().getFullYear()} - <a href="https://github.com/purpxd/E7AutoShop" target='_blank'>Github</a></p>
      </aside>
      <nav className="grid-flow-col gap-4 md:place-self-center md:justify-self-end">
        <div className='flex flex-row gap-2'>
        <button className='btn btn-sm' onClick={() =>  window.pywebview.api.toggleCeciliaBot()}>

          <Book className='text-purple-500' size={20} />
          CeciliaBot</button>
        <a href="https://ko-fi.com/purpxd" target='_blank'>
        <button className='btn btn-sm' >
          <Heart className='text-red-600 fill-red-500' size={20} />
          Donate
        </button>
        </a>
        </div>
      </nav>
    </footer>
  )
}
