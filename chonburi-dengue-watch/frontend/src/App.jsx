import { useEffect, useMemo, useState } from 'react'
import { Activity, AlertTriangle, BarChart3, Bell, CalendarDays, ClipboardPlus, CloudRain, Droplets, Gauge, LayoutDashboard, MapPin, Menu, Stethoscope, Thermometer, Users, Wind } from 'lucide-react'
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api, WS_URL } from './api'

const fallbackDistricts = ['เมืองชลบุรี','บ้านบึง','หนองใหญ่','บางละมุง','พานทอง','พนัสนิคม','ศรีราชา','เกาะสีชัง','สัตหีบ','บ่อทอง','เกาะจันทร์']
const fallbackWeather = ['แจ่มใส','มีเมฆบางส่วน','มีเมฆมาก','ฝนตก','ฝนฟ้าคะนอง']
const today = new Date().toISOString().slice(0, 10)
const initialForm = { district: 'เมืองชลบุรี', record_date: today, period_type: 'weekly', actual_cases: 0, weather_condition: 'มีเมฆมาก', rainfall: 45, temperature: 29, humidity: 76, wind_speed: 8 }
const sampleSeries = [
  {record_date:'ก.ค. W1',actual_cases:18,predicted_cases:16},{record_date:'ก.ค. W2',actual_cases:22,predicted_cases:21},{record_date:'ก.ค. W3',actual_cases:27,predicted_cases:25},{record_date:'ก.ค. W4',actual_cases:24,predicted_cases:29},{record_date:'ส.ค. W1',actual_cases:31,predicted_cases:32},{record_date:'ส.ค. W2',actual_cases:35,predicted_cases:37},{record_date:'ส.ค. W3',actual_cases:39,predicted_cases:41},
]
const sampleAlerts = [
  {district:'บางละมุง',predicted_cases:41,risk_level:'high',rainfall:121.4,record_date:'2026-08-24'},
  {district:'ศรีราชา',predicted_cases:34,risk_level:'high',rainfall:98.2,record_date:'2026-08-24'},
  {district:'เมืองชลบุรี',predicted_cases:22,risk_level:'medium',rainfall:73.8,record_date:'2026-08-24'},
  {district:'สัตหีบ',predicted_cases:13,risk_level:'low',rainfall:51.1,record_date:'2026-08-24'},
]

function StatCard({ icon: Icon, label, value, hint, tone='blue' }) {
  const colors = {blue:'bg-sky-50 text-sky-600',teal:'bg-teal-50 text-teal-600',red:'bg-red-50 text-red-600',indigo:'bg-indigo-50 text-indigo-600'}
  return <div className="card p-5 flex items-start justify-between"><div><p className="text-sm text-slate-500 mb-2">{label}</p><p className="text-3xl font-bold tracking-tight text-slate-800">{value}</p><p className="text-xs text-slate-400 mt-2">{hint}</p></div><div className={`p-3 rounded-xl ${colors[tone]}`}><Icon size={22}/></div></div>
}

function Dashboard({ data }) {
  const series = data ? data.series : sampleSeries
  const alerts = data ? data.alerts : sampleAlerts
  const summary = data ? data.summary : {total_cases:217,predicted_cases:239,high_risk_districts:2,reporting_districts:11}
  return <div className="space-y-6">
    <div className="grid grid-cols-4 gap-4">
      <StatCard icon={Users} label="ผู้ป่วยรายงานล่าสุด" value={`${summary.total_cases} คน`} hint="รวมทุกอำเภอ"/>
      <StatCard icon={Activity} label="คาดการณ์สัปดาห์หน้า" value={`${summary.predicted_cases} คน`} hint="จากโมเดล Random Forest" tone="teal"/>
      <StatCard icon={AlertTriangle} label="พื้นที่เสี่ยงสูง" value={`${summary.high_risk_districts} อำเภอ`} hint="ควรติดตามอย่างใกล้ชิด" tone="red"/>
      <StatCard icon={MapPin} label="พื้นที่ส่งรายงาน" value={`${summary.reporting_districts}/11`} hint="อำเภอในจังหวัดชลบุรี" tone="indigo"/>
    </div>
    <div className="grid grid-cols-[1.55fr_1fr] gap-5">
      <section className="card p-6"><div className="flex justify-between mb-5"><div><h2 className="font-semibold text-slate-800">ผู้ป่วยจริงเทียบค่าพยากรณ์</h2><p className="text-sm text-slate-400 mt-1">แนวโน้มผู้ป่วยรายสัปดาห์</p></div><span className="text-xs bg-sky-50 text-sky-700 px-3 py-2 rounded-lg h-fit">ข้อมูลล่าสุด</span></div>
        <div className="h-72"><ResponsiveContainer><LineChart data={series}><CartesianGrid strokeDasharray="3 3" stroke="#e8f0f5"/><XAxis dataKey="record_date" tick={{fontSize:11}}/><YAxis tick={{fontSize:11}}/><Tooltip/><Legend/><Line type="monotone" dataKey="actual_cases" name="ผู้ป่วยจริง" stroke="#1479b8" strokeWidth={3} dot={{r:3}}/><Line type="monotone" dataKey="predicted_cases" name="ค่าพยากรณ์" stroke="#ef8b45" strokeWidth={3} strokeDasharray="6 4" dot={{r:3}}/></LineChart></ResponsiveContainer></div>
      </section>
      <section className="card p-6"><div className="flex items-center justify-between mb-5"><div><h2 className="font-semibold text-slate-800">การแจ้งเตือนพื้นที่</h2><p className="text-sm text-slate-400 mt-1">เรียงตามระดับความเสี่ยง</p></div><Bell className="text-red-500" size={21}/></div>
        <div className="space-y-3">{alerts.length ? alerts.slice(0,5).map((row) => <div key={row.district} className="border border-slate-100 rounded-xl p-3 flex items-center justify-between"><div className="flex items-center gap-3"><span className={`w-2.5 h-2.5 rounded-full ${row.risk_level==='high'?'bg-red-500':row.risk_level==='medium'?'bg-amber-400':'bg-emerald-500'}`}/><div><p className="font-medium text-sm">อ.{row.district}</p><p className="text-xs text-slate-400">ฝน {row.rainfall} มม.</p></div></div><div className="text-right"><p className="font-semibold text-sm">{row.predicted_cases} คน</p><p className={`text-xs ${row.risk_level==='high'?'text-red-600':row.risk_level==='medium'?'text-amber-600':'text-emerald-600'}`}>{row.risk_level==='high'?'เสี่ยงสูง':row.risk_level==='medium'?'เฝ้าระวัง':'ปกติ'}</p></div></div>) : <p className="text-sm text-slate-400 py-4">ยังไม่มีข้อมูลพื้นที่สำหรับการแจ้งเตือน</p>}</div>
      </section>
    </div>
  </div>
}

function AnalyticsReport({ data }) {
  const series = data ? data.series : sampleSeries
  const alerts = data ? data.alerts : sampleAlerts
  const summary = data ? data.summary : { total_cases: 217, predicted_cases: 239, high_risk_districts: 2, reporting_districts: 11 }
  const totalsByDate = new Map()
  series.forEach(row => totalsByDate.set(row.record_date, (totalsByDate.get(row.record_date) || 0) + Number(row.actual_cases || 0)))
  const timeline = [...totalsByDate].sort(([left], [right]) => left.localeCompare(right)).map(([record_date, actual_cases]) => ({ record_date, actual_cases }))
  const totalReports = series.length
  const averageCases = timeline.length ? Math.round(timeline.reduce((sum, row) => sum + row.actual_cases, 0) / timeline.length) : 0
  const peak = timeline.reduce((highest, row) => !highest || row.actual_cases > highest.actual_cases ? row : highest, null)
  const trend = timeline.length > 1 ? timeline.at(-1).actual_cases - timeline[0].actual_cases : 0
  return <div className="space-y-6">
    <div className="grid grid-cols-4 gap-4">
      <StatCard icon={Users} label="ผู้ป่วยสะสม" value={`${summary.total_cases} คน`} hint="จากข้อมูลล่าสุด" />
      <StatCard icon={Gauge} label="ค่าเฉลี่ยต่อรายงาน" value={`${averageCases} คน`} hint={`${totalReports} รายการรายงาน`} tone="teal" />
      <StatCard icon={AlertTriangle} label="แนวโน้มช่วงล่าสุด" value={`${trend >= 0 ? '+' : ''}${trend} คน`} hint="เทียบต้นช่วงข้อมูล" tone={trend > 0 ? 'red' : 'blue'} />
      <StatCard icon={MapPin} label="พื้นที่เสี่ยงสูง" value={`${summary.high_risk_districts} อำเภอ`} hint="จากการประเมินล่าสุด" tone="indigo" />
    </div>
    <div className="grid grid-cols-[1.55fr_1fr] gap-5">
      <section className="card p-6"><div className="flex justify-between mb-5"><div><h2 className="font-semibold text-slate-800">วิเคราะห์แนวโน้มผู้ป่วย</h2><p className="text-sm text-slate-400 mt-1">เปรียบเทียบผู้ป่วยจริงกับค่าพยากรณ์ตามช่วงเวลา</p></div><BarChart3 className="text-sky-600" size={21}/></div>
        <div className="h-80"><ResponsiveContainer><LineChart data={series}><CartesianGrid strokeDasharray="3 3" stroke="#e8f0f5"/><XAxis dataKey="record_date" tick={{fontSize:11}}/><YAxis tick={{fontSize:11}}/><Tooltip/><Legend/><Line type="monotone" dataKey="actual_cases" name="ผู้ป่วยจริง" stroke="#1479b8" strokeWidth={3} dot={{r:3}}/><Line type="monotone" dataKey="predicted_cases" name="ค่าพยากรณ์" stroke="#ef8b45" strokeWidth={3} strokeDasharray="6 4" dot={{r:3}}/></LineChart></ResponsiveContainer></div>
      </section>
      <section className="card p-6"><div className="flex items-center justify-between mb-5"><div><h2 className="font-semibold text-slate-800">ข้อค้นพบสำคัญ</h2><p className="text-sm text-slate-400 mt-1">สรุปสำหรับการติดตามสถานการณ์</p></div><Activity className="text-teal-600" size={21}/></div>
        <div className="space-y-4 text-sm"><div className="border-l-4 border-sky-500 bg-sky-50 rounded-r-lg p-4"><p className="font-semibold text-slate-800">จุดสูงสุดของผู้ป่วย</p><p className="text-slate-500 mt-1">{peak?.record_date || '-'} จำนวน {peak?.actual_cases || 0} คน</p></div><div className={`border-l-4 rounded-r-lg p-4 ${trend > 0 ? 'border-red-500 bg-red-50' : 'border-emerald-500 bg-emerald-50'}`}><p className="font-semibold text-slate-800">ทิศทางสถานการณ์</p><p className="text-slate-500 mt-1">{trend > 0 ? 'จำนวนผู้ป่วยมีแนวโน้มเพิ่มขึ้น ควรติดตามพื้นที่เสี่ยงใกล้ชิด' : 'จำนวนผู้ป่วยทรงตัวหรือลดลงจากต้นช่วงข้อมูล'}</p></div><div className="border-l-4 border-amber-400 bg-amber-50 rounded-r-lg p-4"><p className="font-semibold text-slate-800">พื้นที่ที่ควรเฝ้าระวัง</p><p className="text-slate-500 mt-1">{alerts.filter(row => row.risk_level === 'high').map(row => `อ.${row.district}`).join(', ') || 'ยังไม่พบพื้นที่เสี่ยงสูง'}</p></div></div>
      </section>
    </div>
  </div>
}

function DataForm({ config, onSaved, onReset }) {
  const [form,setForm] = useState(initialForm), [status,setStatus] = useState(null), [saving,setSaving] = useState(false)
  const fields = [{key:'rainfall',label:'ปริมาณน้ำฝน',unit:'มม.',icon:CloudRain},{key:'temperature',label:'อุณหภูมิ',unit:'°C',icon:Thermometer},{key:'humidity',label:'ความชื้น',unit:'%',icon:Droplets},{key:'wind_speed',label:'ความเร็วลม',unit:'กม./ชม.',icon:Wind}]
  const set = (key,value) => setForm(f=>({...f,[key]:value}))
  const submit = async e => { e.preventDefault(); setSaving(true); setStatus({ok:null,text:'กำลังบันทึกและวิเคราะห์ข้อมูล...' }); try { const payload={...form,actual_cases:Number(form.actual_cases),rainfall:Number(form.rainfall),temperature:Number(form.temperature),humidity:Number(form.humidity),wind_speed:Number(form.wind_speed)}; const result=await api.createObservation(payload); setStatus({ok:true,text:`บันทึกแล้ว • คาดการณ์ ${result.prediction.predicted_cases} คน (${result.prediction.risk_label})`}); onSaved() } catch(err) {setStatus({ok:false,text:err.message})} finally {setSaving(false)} }
  const resetAll = async () => { if (!window.confirm('ยืนยันครั้งที่ 1: ต้องการล้างข้อมูลการเฝ้าระวังทั้งหมดใช่หรือไม่?')) return; if (!window.confirm('ยืนยันครั้งที่ 2: ข้อมูลทั้งหมดจะถูกลบถาวรและไม่สามารถกู้คืนได้ ดำเนินการต่อหรือไม่?')) return; const adminToken = window.prompt('กรอกรหัสผู้ดูแลระบบเพื่อยืนยันการลบ'); if (!adminToken) return; setSaving(true); setStatus(null); try { const result = await api.resetObservations(adminToken); setForm(initialForm); setStatus({ok:true,text:`รีเซ็ตข้อมูลเรียบร้อยแล้ว ${result.deleted_count} รายการ`}); onReset() } catch(err) { setStatus({ok:false,text:err.message}) } finally { setSaving(false) } }
  return <div className="max-w-5xl"><div className="card overflow-hidden"><div className="px-7 py-6 bg-gradient-to-r from-sky-700 to-cyan-600 text-white"><div className="flex gap-3 items-center"><ClipboardPlus/><div><h2 className="text-xl font-semibold">บันทึกข้อมูลเฝ้าระวัง</h2><p className="text-sky-100 text-sm mt-1">กรอกข้อมูลผู้ป่วยและสภาพอากาศตามรอบรายงาน</p></div></div></div>
    <form className="p-7 space-y-7" onSubmit={submit}><div><h3 className="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2"><CalendarDays size={17} className="text-sky-600"/>ข้อมูลรอบรายงาน</h3><div className="grid grid-cols-3 gap-5"><label className="text-sm">อำเภอ<select className="field mt-2" value={form.district} onChange={e=>set('district',e.target.value)}>{config.districts.map(d=><option key={d}>{d}</option>)}</select></label><label className="text-sm">วันที่รายงาน<input className="field mt-2" type="date" value={form.record_date} onChange={e=>set('record_date',e.target.value)} required/></label><label className="text-sm">รอบข้อมูล<select className="field mt-2" value={form.period_type} onChange={e=>set('period_type',e.target.value)}><option value="weekly">รายสัปดาห์</option><option value="monthly">รายเดือน</option></select></label></div></div>
    <div className="border-t border-slate-100 pt-6"><h3 className="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2"><Stethoscope size={17} className="text-sky-600"/>ข้อมูลระบาดวิทยา</h3><label className="text-sm block max-w-xs">จำนวนผู้ป่วยไข้เลือดออก (คน)<input className="field mt-2" type="number" min="0" value={form.actual_cases} onChange={e=>set('actual_cases',e.target.value)} required/></label></div>
    <div className="border-t border-slate-100 pt-6"><h3 className="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2"><CloudRain size={17} className="text-sky-600"/>ข้อมูลสภาพอากาศ</h3><div className="grid grid-cols-3 gap-5"><label className="text-sm">สภาพอากาศทั่วไป<select className="field mt-2" value={form.weather_condition} onChange={e=>set('weather_condition',e.target.value)}>{config.weather_options.map(w=><option key={w}>{w}</option>)}</select></label>{fields.map(({key,label,unit,icon:Icon})=>{ const limits={rainfall:[0,1000],temperature:[10,50],humidity:[0,100],wind_speed:[0,200]}; return <label key={key} className="text-sm">{label} ({unit})<div className="relative mt-2"><Icon size={16} className="absolute left-3 top-3 text-slate-400"/><input className="field pl-9 pr-9 text-center" type="number" step="0.1" min={limits[key][0]} max={limits[key][1]} value={form[key]} onChange={e=>set(key,e.target.value)} required/></div></label>})}</div></div>
    {status&&<div className={`rounded-xl p-4 text-sm ${status.ok===true?'bg-emerald-50 text-emerald-700':status.ok===null?'bg-sky-50 text-sky-700':'bg-red-50 text-red-700'}`}>{status.text}</div>}<div className="flex justify-between items-center gap-4"><button type="button" onClick={resetAll} disabled={saving} className="border border-red-200 text-red-600 hover:bg-red-50 disabled:opacity-50 px-5 py-3 rounded-xl font-medium">รีเซ็ตข้อมูลทั้งหมด</button><button disabled={saving} className="bg-sky-700 hover:bg-sky-800 disabled:opacity-50 text-white px-6 py-3 rounded-xl font-medium shadow-sm">{saving?'กำลังบันทึก...':'บันทึกและวิเคราะห์ความเสี่ยง'}</button></div></form></div></div>
}

function formatLiveTimestamp(value) {
  if (!value) return 'ยังไม่อัปเดต'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'กำลังอัปเดต'
  return new Intl.DateTimeFormat('th-TH', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
}

function formatUpdatedAgoThai(value) {
  if (!value) return 'อัปเดตเมื่อสักครู่'
  const diffSeconds = Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 1000))
  if (diffSeconds < 60) return `อัปเดต ${diffSeconds} วินาทีที่แล้ว`
  if (diffSeconds < 3600) return `อัปเดต ${Math.floor(diffSeconds / 60)} นาทีที่แล้ว`
  return `อัปเดต ${Math.floor(diffSeconds / 3600)} ชั่วโมงที่แล้ว`
}

export default function App() {
  const [page,setPage]=useState('dashboard'), [data,setData]=useState(null), [connected,setConnected]=useState(false), [config,setConfig]=useState({districts:fallbackDistricts,weather_options:fallbackWeather}), [lastUpdated,setLastUpdated]=useState(null), [updatedAgo,setUpdatedAgo]=useState('อัปเดตเมื่อสักครู่')
  const refresh=async()=>{ try { const dashboardData=await api.dashboard(); setData(dashboardData); setLastUpdated(dashboardData.updated_at || new Date().toISOString()); setConnected(true); } catch { setConnected(false) } }
  useEffect(()=>{ api.config().then(c=>setConfig(c)).catch(()=>{}); refresh(); const timer = setInterval(refresh, 15000); return ()=>clearInterval(timer) },[])
  useEffect(()=>{
    const syncAgo = () => setUpdatedAgo(formatUpdatedAgoThai(lastUpdated))
    syncAgo()
    const timer = setInterval(syncAgo, 1000)
    return ()=>clearInterval(timer)
  }, [lastUpdated])

  useEffect(()=>{
    let socket
    let reconnectTimer
    let stopped = false
    const connect = () => {
      if (stopped) return
      socket = new WebSocket(WS_URL)
      socket.onopen = () => setConnected(true)
      socket.onmessage = async (event) => {
        try {
          const payload = JSON.parse(event.data)
          if (payload.event === 'dashboard' && payload.updated_at) {
            setLastUpdated(payload.updated_at)
            setConnected(true)
            await refresh()
          }
        } catch {
          setConnected(false)
          socket.close()
        }
      }
      socket.onclose = () => {
        if (!stopped) {
          setConnected(false)
          reconnectTimer = setTimeout(connect, 3000)
        }
      }
      socket.onerror = () => socket.close()
    }
    connect()
    return ()=>{
      stopped = true
      clearTimeout(reconnectTimer)
      socket?.close()
    }
  }, [])

  const title=useMemo(()=>page==='dashboard'?'ภาพรวมสถานการณ์':page==='form'?'บันทึกข้อมูลประจำงวด':'รายงานเชิงวิเคราะห์',[page])
  return <div className="min-h-screen flex"><aside className="w-64 bg-[#0b3d62] text-white fixed inset-y-0 left-0"><div className="h-20 px-6 flex items-center gap-3 border-b border-white/10"><div className="bg-cyan-400/20 p-2 rounded-xl"><Activity className="text-cyan-300"/></div><div><p className="font-semibold">Dengue Watch</p><p className="text-xs text-sky-200">จังหวัดชลบุรี</p></div></div><nav className="p-4 space-y-2"><p className="text-[11px] uppercase tracking-widest text-sky-300 px-3 py-3">เมนูหลัก</p><button onClick={()=>setPage('dashboard')} className={`w-full flex gap-3 items-center px-4 py-3 rounded-xl text-sm ${page==='dashboard'?'bg-white/15 text-white':'text-sky-100 hover:bg-white/10'}`}><LayoutDashboard size={19}/>ภาพรวมสถานการณ์</button><button onClick={()=>setPage('form')} className={`w-full flex gap-3 items-center px-4 py-3 rounded-xl text-sm ${page==='form'?'bg-white/15 text-white':'text-sky-100 hover:bg-white/10'}`}><ClipboardPlus size={19}/>บันทึกข้อมูล</button><button onClick={()=>setPage('analytics')} className={`w-full flex gap-3 items-center px-4 py-3 rounded-xl text-sm ${page==='analytics'?'bg-white/15 text-white':'text-sky-100 hover:bg-white/10'}`}><BarChart3 size={19}/>รายงานเชิงวิเคราะห์</button></nav><div className="absolute bottom-5 left-4 right-4 bg-white/10 rounded-xl p-4"><div className="flex items-center gap-2 text-sm"><span className={`inline-block w-2.5 h-2.5 rounded-full ${connected ? 'bg-emerald-400 animate-pulse shadow-[0_0_10px_rgba(52,211,153,0.9)]' : 'bg-amber-400'}`}/><span className="tracking-wide">{connected ? 'LIVE' : 'OFFLINE'}</span></div><div className="mt-2 inline-flex items-center px-2 py-1 rounded-full bg-sky-500/20 text-xs text-sky-100 border border-sky-200/20">{updatedAgo}</div><p className="text-xs text-sky-200 mt-2">อัปเดตล่าสุด: {formatLiveTimestamp(lastUpdated)}</p></div></aside>
  <main className="ml-64 flex-1"><header className="h-20 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-10"><div><h1 className="text-xl font-bold text-slate-800">{title}</h1><p className="text-sm text-slate-400">ระบบเฝ้าระวังและพยากรณ์โรคไข้เลือดออก</p></div><div className="flex items-center gap-4"><button className="p-2.5 rounded-xl bg-slate-50 text-slate-500"><Bell size={19}/></button><div className="h-9 w-px bg-slate-200"/><div className="text-right"><p className="text-sm font-medium">เจ้าหน้าที่สาธารณสุข</p><p className="text-xs text-slate-400">สำนักงานสาธารณสุขจังหวัดชลบุรี</p></div><div className="w-10 h-10 rounded-full bg-sky-100 text-sky-700 grid place-items-center font-bold">สธ</div></div></header><div className="p-8">{page==='dashboard'?<Dashboard data={data}/>:page==='analytics'?<AnalyticsReport data={data}/>:<DataForm config={config} onSaved={()=>{refresh();setTimeout(()=>setPage('dashboard'),700)}} onReset={()=>{refresh();setPage('form')}}/>}</div></main></div>
}
