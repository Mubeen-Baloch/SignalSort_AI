'use client';

import Link from 'next/link';
import {usePathname,useRouter} from 'next/navigation';
import {Bell,Grid2X2,LogOut,MessagesSquare,Target,Upload} from 'lucide-react';

const links=[
  {href:'/dashboard',label:'Dashboard',icon:Grid2X2},
  {href:'/ingest',label:'Ingest',icon:Upload},
  {href:'/intents',label:'Intents',icon:Target},
  {href:'/messages',label:'Messages',icon:MessagesSquare},
];

function Logo({compact=false}:{compact?:boolean}){return <Link href="/dashboard" className={`flex shrink-0 items-center gap-2 whitespace-nowrap font-bold ${compact?'text-base':'text-lg'}`}><span className="flex h-5 items-end gap-0.5"><i className="block w-1 rounded bg-[var(--accent)]" style={{height:8}}/><i className="block w-1 rounded bg-[var(--accent)]" style={{height:18}}/><i className="block w-1 rounded bg-[var(--accent)]" style={{height:12}}/></span><span className="text-[var(--text)]">SignalSort<span className="hidden sm:inline"> AI</span></span></Link>}

export default function Shell({children}:{children:React.ReactNode}){const pathname=usePathname(),router=useRouter();const title=links.find(link=>link.href===pathname)?.label||'Dashboard';return <div className="min-h-dvh bg-[var(--bg)] text-[var(--text)] md:flex"><aside className="sticky top-0 hidden h-dvh w-[240px] shrink-0 flex-col border-r border-[var(--border)] p-3 md:flex"><div className="px-2 pb-4 pt-1"><Logo/></div><nav className="flex flex-col gap-1">{links.map(({href,label,icon:Icon})=>{const active=pathname===href;return <Link key={href} href={href} className={`flex min-h-11 items-center gap-3 rounded-[10px] px-3 text-sm font-medium transition ${active?'bg-[var(--surface-2)] text-[var(--text)]':'text-[var(--muted)] hover:bg-[var(--surface-2)] hover:text-[var(--text)]'}`}><Icon className={active?'text-[var(--accent)]':''} size={18}/><span>{label}</span></Link>})}</nav><div className="flex-1"/><button className="secondary justify-start" onClick={()=>{localStorage.removeItem('token');router.push('/login')}}><LogOut size={18}/>Log out</button></aside><div className="min-w-0 flex-1"><header className="sticky top-0 z-20 flex items-center gap-3 border-b border-[var(--border)] bg-[var(--bg)] px-4 py-3 md:px-6"><div className="md:hidden"><Logo compact/></div><h1 className="hidden flex-1 text-xl font-bold md:block">{title}</h1><button className="grid h-11 w-11 shrink-0 place-items-center rounded-[10px] border border-[var(--border)] bg-[var(--surface)]" title="Notifications" onClick={()=>router.push('/dashboard#notifications')}><Bell size={19}/></button></header><main className="mx-auto max-w-[1200px] px-4 py-5 pb-24 md:px-6 md:py-6">{children}</main></div><nav className="fixed inset-x-0 bottom-0 z-30 grid h-14 grid-cols-4 border-t border-[var(--border)] bg-[var(--surface)] md:hidden">{links.map(({href,label,icon:Icon})=>{const active=pathname===href;return <Link key={href} href={href} className={`relative flex flex-col items-center justify-center gap-0.5 text-[11px] ${active?'text-[var(--accent)]':'text-[var(--muted)]'}`}>{active&&<span className="absolute top-0 h-0.5 w-6 rounded bg-[var(--accent)]"/>}<Icon size={17}/><span>{label}</span></Link>})}</nav></div>}
