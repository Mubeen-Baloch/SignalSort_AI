'use client';

import {useEffect,useState} from 'react';
import {Search} from 'lucide-react';
import Shell from '../../components/Shell';
import {api} from '../../lib/api';

const categories=['Opportunity/Collaboration','Job/Internship','Event/Announcement','Resource/Learning','Question/Help','Discussion','Social/Noise'];
const colors=['#c6f432','#5cc8ff','#ffb547','#b79cff','#ff8fa3'];
function initials(name:string){return name.split(' ').map(part=>part[0]).join('').slice(0,2).toUpperCase()}
function avatarColor(name:string){return colors[[...name].reduce((sum,char)=>sum+char.charCodeAt(0),0)%colors.length]}

export default function Messages(){const [items,setItems]=useState<any[]>([]),[search,setSearch]=useState(''),[category,setCategory]=useState('');useEffect(()=>{api('/messages?limit=100').then(setItems)},[]);const filtered=items.filter(x=>(!search||x.text.toLowerCase().includes(search.toLowerCase()))&&(!category||x.category===category));return <Shell><div className="mb-5"><h2 className="text-2xl font-bold md:text-[28px]">Messages</h2><p className="muted mt-1">Search the classified source messages behind your matches.</p></div><div className="panel mb-5 grid gap-3 md:grid-cols-[minmax(0,1fr)_260px]"><label className="relative block"><Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--muted)]" size={18}/><input className="pl-10" placeholder="Search messages" value={search} onChange={e=>setSearch(e.target.value)}/></label><select value={category} onChange={e=>setCategory(e.target.value)}><option value="">All categories</option>{categories.map(item=><option key={item}>{item}</option>)}</select></div><section className="space-y-2">{filtered.map(item=><article className="card flex gap-3" key={item.id}><div className="grid h-10 w-10 shrink-0 place-items-center rounded-full text-sm font-bold text-[var(--accent-ink)]" style={{background:avatarColor(item.sender||'Unknown')}}>{initials(item.sender||'U')}</div><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center justify-between gap-2"><b>{item.sender}</b><span className="badge bg-[color:color-mix(in_srgb,var(--info)_16%,transparent)] text-[var(--info)]">{item.category}</span></div><p className="mt-2 leading-relaxed">{item.text}</p></div></article>)}{!filtered.length&&<div className="card py-12 text-center"><Search className="mx-auto mb-3 text-[var(--accent)]" size={30}/><p className="muted">No messages match. Try a different search or category.</p></div>}</section></Shell>}
