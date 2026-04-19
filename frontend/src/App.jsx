import { useState } from "react"

const API = "http://localhost:8000/api"

const EXAMPLE = {
  relation_name: "R",
  attributes: ["A", "B", "C", "D", "E"],
  functional_dependencies: [
    { lhs: ["A", "B"], rhs: ["C"] },
    { lhs: ["C"],      rhs: ["D"] },
    { lhs: ["D"],      rhs: ["E"] },
  ],
  multivalued_dependencies: [],
  join_dependencies: [],
  target_nf: "BCNF",
}

const C = {
  bg:         "#0a0d14",
  surface:    "#111520",
  card:       "#161b2e",
  border:     "#232b45",
  borderHi:   "#2e3a5c",
  accent:     "#4f8ef7",
  accentDim:  "#1e3a7a",
  accentGlow: "#4f8ef722",
  teal:       "#0ecf9a",
  tealDim:    "#063d2c",
  tealGlow:   "#0ecf9a18",
  purple:     "#a78bfa",
  purpleDim:  "#2d1f5e",
  amber:      "#fbbf24",
  amberDim:   "#3d2a00",
  text:       "#dde3f5",
  textMid:    "#7d8ab0",
  textDim:    "#424d6e",
  lhsBg:      "#162050",
  lhsText:    "#7aa2ff",
  rhsBg:      "#072e1f",
  rhsText:    "#3ecfa0",
  error:      "#f87171",
  errorBg:    "#2d0f0f",
  errorBorder:"#7f1d1d",
}

const PHASE_GROUPS = {
  "BCNF": {
    label: "dek_BCNF",
    color: C.accent,
    phases: ["init", "bcnf_ok", "decompose", "split", "done"],
  },
  "UNION": {
    label: "Unija",
    color: C.teal,
    phases: ["init_union", "merge", "no_merge", "done_union"],
  },
  "4NF": {
    label: "dek_4NF",
    color: C.purple,
    phases: ["init_4nf", "4nf_ok", "4nf_violation", "4nf_split", "done_4nf"],
  },
  "5NF": {
    label: "dek_5NF",
    color: C.amber,
    phases: ["init_5nf", "5nf_ok", "5nf_violation", "5nf_split", "5nf_split_component", "done_5nf"],
  },
}

// Grupišemo korake po fazama — BCNF i UNION dijele init/done pa ih razlikujemo po poziciji
function groupSteps(steps) {
  const groups = { BCNF: [], UNION: [], "4NF": [], "5NF": [] }
  let bcnfDone = false

  for (const step of steps) {
    const p = step.phase

    if (["init_4nf","4nf_ok","4nf_violation","4nf_split","done_4nf"].includes(p)) {
      groups["4NF"].push(step)
    } else if (["init_5nf","5nf_ok","5nf_violation","5nf_split","5nf_split_component","done_5nf"].includes(p)) {
      groups["5NF"].push(step)
    } else if (["merge","no_merge"].includes(p)) {
      groups.UNION.push(step)
    } else if (p === "done" && bcnfDone) {
      // drugi "done" je kraj unije
      groups.UNION.push(step)
    } else if (p === "init" && bcnfDone) {
      groups.UNION.push(step)
    } else {
      if (p === "done") bcnfDone = true
      groups.BCNF.push(step)
    }
  }
  return groups
}

function stepIcon(phase) {
  if (phase.includes("ok"))        return "✓"
  if (phase.includes("violation")) return "✗"
  if (phase === "decompose")       return "⊢"
  if (phase === "split" || phase.includes("split")) return "⊣⊢"
  if (phase === "merge")           return "∪"
  if (phase === "no_merge")        return "—"
  if (phase.includes("init"))      return "▶"
  if (phase.includes("done"))      return "■"
  if (phase.includes("component")) return "·"
  return "·"
}

function stepAccentColor(phase, groupColor) {
  if (phase.includes("ok"))        return C.teal
  if (phase.includes("violation")) return C.error
  if (phase.includes("done"))      return groupColor
  if (phase.includes("init"))      return C.textMid
  return C.text
}

// ══════════════════════════════════════════════════════════════════════════
export default function App() {
  const [relationName, setRelationName] = useState(EXAMPLE.relation_name)
  const [attrsInput, setAttrsInput]     = useState(EXAMPLE.attributes.join(", "))
  const [fds, setFds]                   = useState(EXAMPLE.functional_dependencies)
  const [mvds, setMvds]                 = useState([])
  const [jds, setJds]                   = useState([])
  const [targetNf, setTargetNf]         = useState("BCNF")

  const [lhsInput, setLhsInput]         = useState("")
  const [rhsInput, setRhsInput]         = useState("")
  const [mvdLhs, setMvdLhs]             = useState("")
  const [mvdRhs, setMvdRhs]             = useState("")
  const [jdInput, setJdInput]           = useState("")

  const [result, setResult]             = useState(null)
  const [error, setError]               = useState(null)
  const [loading, setLoading]           = useState(false)
  const [activeTab, setActiveTab]       = useState(null)

  function addFd() {
    const lhs = lhsInput.split(",").map(s => s.trim().toUpperCase()).filter(Boolean)
    const rhs = rhsInput.split(",").map(s => s.trim().toUpperCase()).filter(Boolean)
    if (!lhs.length || !rhs.length) return
    setFds(prev => [...prev, { lhs, rhs }])
    setLhsInput(""); setRhsInput("")
  }

  function addMvd() {
    const lhs = mvdLhs.split(",").map(s => s.trim().toUpperCase()).filter(Boolean)
    const rhs = mvdRhs.split(",").map(s => s.trim().toUpperCase()).filter(Boolean)
    if (!lhs.length || !rhs.length) return
    setMvds(prev => [...prev, { lhs, rhs }])
    setMvdLhs(""); setMvdRhs("")
  }

  function addJd() {
    const raw = jdInput.trim()
    if (!raw) return
    const components = raw.split("|").map(part =>
      part.split(",").map(s => s.trim().toUpperCase()).filter(Boolean)
    ).filter(c => c.length > 0)
    if (components.length < 2) return
    setJds(prev => [...prev, { components }])
    setJdInput("")
  }

  async function handleSubmit() {
    setError(null); setResult(null); setLoading(true); setActiveTab(null)
    const attributes = attrsInput.split(",").map(s => s.trim().toUpperCase()).filter(Boolean)
    const payload = {
      relation_name: relationName.toUpperCase(),
      attributes,
      functional_dependencies: fds,
      multivalued_dependencies: mvds,
      join_dependencies: jds,
      target_nf: targetNf,
    }
    try {
      const res = await fetch(`${API}/decompose`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(JSON.stringify(err.detail))
      }
      const data = await res.json()
      setResult(data)
      const grouped = groupSteps(data.steps)
      const first = ["BCNF","UNION","4NF","5NF"].find(g => grouped[g].length > 0)
      setActiveTab(first || "BCNF")
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function handleReset() {
    setRelationName(EXAMPLE.relation_name)
    setAttrsInput(EXAMPLE.attributes.join(", "))
    setFds(EXAMPLE.functional_dependencies)
    setMvds([]); setJds([])
    setTargetNf("BCNF")
    setResult(null); setError(null)
  }

  return (
    <div style={s.page}>
      <div style={s.bgGlow1} />
      <div style={s.bgGlow2} />
      <div style={s.container}>

        <header style={s.header}>
          <div style={s.headerBar} />
          <div>
            <h1 style={s.title}>Dekompozicija šeme relacije</h1>
            <p style={s.subtitle}>
              Unesi skup obeležja i zavisnosti — alat prikazuje korake dekompozicije do željene normalne forme.
            </p>
          </div>
        </header>

        {/* Osnovna polja + NF */}
        <section style={s.card}>
          <div style={s.cardRow}>
            <div style={s.fieldCol}>
              <label style={s.label}>Ime relacije</label>
              <input style={{...s.input, width: 90}} value={relationName}
                onChange={e => setRelationName(e.target.value)} placeholder="R" maxLength={10} />
            </div>
            <div style={{...s.fieldCol, flex:1}}>
              <label style={s.label}>Skup obeležja <span style={s.hint}>(odvojeni zarezom)</span></label>
              <input style={s.input} value={attrsInput}
                onChange={e => setAttrsInput(e.target.value)} placeholder="A, B, C, D, E" />
            </div>
          </div>
          <div style={{marginTop: 20}}>
            <label style={s.label}>Ciljna normalna forma</label>
            <div style={s.nfGroup}>
              {["BCNF","4NF","5NF"].map(nf => (
                <button key={nf}
                  style={targetNf === nf ? s.nfActive : s.nfBtn}
                  onClick={() => setTargetNf(nf)}>
                  {nf}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* FZ */}
        <section style={s.card}>
          <p style={s.sectionTitle}>Funkcionalne zavisnosti</p>
          <DepList items={fds} onRemove={i => setFds(p => p.filter((_,x) => x !== i))}
            render={fd => <><Chip v="lhs">{fd.lhs.join(", ")}</Chip><Arrow>→</Arrow><Chip v="rhs">{fd.rhs.join(", ")}</Chip></>} />
          <AddRow
            left={<input style={s.ifd} value={lhsInput} onChange={e=>setLhsInput(e.target.value)}
              placeholder="Leva strana  (A, B)" onKeyDown={e=>e.key==="Enter"&&addFd()} />}
            sep={<Arrow>→</Arrow>}
            right={<input style={s.ifd} value={rhsInput} onChange={e=>setRhsInput(e.target.value)}
              placeholder="Desna strana  (C)" onKeyDown={e=>e.key==="Enter"&&addFd()} />}
            onAdd={addFd} />
        </section>

        {/* MVD */}
        {(targetNf === "4NF" || targetNf === "5NF") && (
          <section style={{...s.card, borderColor: C.purple+"55"}}>
            <div style={s.secRow}>
              <p style={{...s.sectionTitle, color: C.purple, margin:0}}>Višeznačne zavisnosti (MVD)</p>
              <span style={s.hint}>X ↠ Y</span>
            </div>
            <DepList items={mvds} onRemove={i => setMvds(p=>p.filter((_,x)=>x!==i))}
              empty="Nema MVD — dodaj ako postoje višeznačne zavisnosti."
              render={m => <><Chip v="lhs">{m.lhs.join(", ")}</Chip><Arrow c={C.purple}>↠</Arrow><Chip v="rhs">{m.rhs.join(", ")}</Chip></>} />
            <AddRow
              left={<input style={s.ifd} value={mvdLhs} onChange={e=>setMvdLhs(e.target.value)}
                placeholder="Leva strana  (kurs)" onKeyDown={e=>e.key==="Enter"&&addMvd()} />}
              sep={<Arrow c={C.purple}>↠</Arrow>}
              right={<input style={s.ifd} value={mvdRhs} onChange={e=>setMvdRhs(e.target.value)}
                placeholder="Desna strana  (nastavnik)" onKeyDown={e=>e.key==="Enter"&&addMvd()} />}
              onAdd={addMvd} btnColor={C.purple} />
          </section>
        )}

        {/* JD */}
        {targetNf === "5NF" && (
          <section style={{...s.card, borderColor: C.amber+"55"}}>
            <div style={s.secRow}>
              <p style={{...s.sectionTitle, color: C.amber, margin:0}}>Zavisnosti spajanja (JD)</p>
              <span style={s.hint}>komponente odvojene sa  |</span>
            </div>
            <DepList items={jds} onRemove={i => setJds(p=>p.filter((_,x)=>x!==i))}
              empty="Nema JD — dodaj ako postoje zavisnosti spajanja."
              render={jd => (
                <div style={{display:"flex",gap:6,flexWrap:"wrap",alignItems:"center"}}>
                  <span style={{color:C.amber,fontSize:13}}>⊳◁</span>
                  {jd.components.map((c,ci) => (
                    <span key={ci} style={{display:"flex",alignItems:"center",gap:4}}>
                      <Chip v="amber">{c.join(", ")}</Chip>
                      {ci < jd.components.length-1 && <span style={{color:C.textDim}}>|</span>}
                    </span>
                  ))}
                </div>
              )} />
            <div style={s.addRow}>
              <input style={{...s.ifd,flex:1}} value={jdInput}
                onChange={e=>setJdInput(e.target.value)}
                placeholder="npr.  A, B | B, C | A, C"
                onKeyDown={e=>e.key==="Enter"&&addJd()} />
              <AddBtn onClick={addJd} color={C.amber} />
            </div>
            <p style={{...s.hint, fontSize:11, marginTop:6}}>
              Zarez = atributi unutar komponente · Pipe (|) = razdvaja komponente
            </p>
          </section>
        )}

        {/* Akcije */}
        <div style={s.actions}>
          <button style={s.btnPrimary} onClick={handleSubmit} disabled={loading}>
            {loading
              ? <span style={{display:"flex",alignItems:"center",gap:8}}><Spin/>Obrađujem...</span>
              : "Dekomponuj →"}
          </button>
          <button style={s.btnSec} onClick={handleReset}>Resetuj</button>
        </div>

        {error && (
          <div style={s.errBox}>
            <span style={{fontSize:15}}>⚠</span>
            <span>{error}</span>
          </div>
        )}

        {result && (
          <ResultPanel result={result} activeTab={activeTab} setActiveTab={setActiveTab} />
        )}

      </div>
    </div>
  )
}

// ── Pomoćne komponente ────────────────────────────────────────────────────

function Chip({ v, children }) {
  const cfg = {
    lhs:   [C.lhsBg,    C.lhsText],
    rhs:   [C.rhsBg,    C.rhsText],
    amber: [C.amberDim, C.amber],
    key:   [C.accentDim,C.accent],
  }[v] || [C.lhsBg, C.lhsText]
  return (
    <span style={{background:cfg[0],color:cfg[1],padding:"3px 10px",borderRadius:5,
      fontSize:13,fontWeight:600,letterSpacing:"0.04em",fontFamily:"inherit"}}>
      {children}
    </span>
  )
}

function Arrow({ c = C.textMid, children }) {
  return <span style={{color:c,fontSize:15,flexShrink:0}}>{children}</span>
}

function AddBtn({ onClick, color = C.accent }) {
  return (
    <button onClick={onClick} style={{background:color+"22",border:`1px solid ${color}66`,
      borderRadius:8,color,fontSize:13,fontWeight:600,fontFamily:"inherit",
      padding:"9px 18px",cursor:"pointer",whiteSpace:"nowrap",letterSpacing:"0.03em"}}>
      + Dodaj
    </button>
  )
}

function DepList({ items, onRemove, render, empty="Još nema unetih zavisnosti." }) {
  return (
    <div style={{display:"flex",flexDirection:"column",gap:6,marginBottom:14,minHeight:34}}>
      {items.length === 0
        ? <p style={{fontSize:12,color:C.textDim,margin:0,fontStyle:"italic",padding:"4px 0"}}>{empty}</p>
        : items.map((item,i) => (
            <div key={i} style={{display:"flex",alignItems:"center",gap:10,
              background:C.surface,border:`1px solid ${C.border}`,borderRadius:8,padding:"7px 12px"}}>
              <div style={{display:"flex",alignItems:"center",gap:8,flex:1,flexWrap:"wrap"}}>
                {render(item)}
              </div>
              <button onClick={()=>onRemove(i)}
                style={{background:"transparent",border:"none",color:C.textDim,
                  fontSize:17,cursor:"pointer",padding:"0 2px",fontFamily:"inherit"}}>×</button>
            </div>
          ))
      }
    </div>
  )
}

function AddRow({ left, sep, right, onAdd, btnColor }) {
  return (
    <div style={s.addRow}>
      <div style={{display:"flex",alignItems:"center",gap:8,flex:1,minWidth:0}}>
        {left}{sep}{right}
      </div>
      <AddBtn onClick={onAdd} color={btnColor} />
    </div>
  )
}

function Spin() {
  return <span style={{width:13,height:13,border:"2px solid #ffffff44",
    borderTopColor:"#fff",borderRadius:"50%",animation:"spin 0.7s linear infinite",
    display:"inline-block"}} />
}

// ── Panel rezultata ───────────────────────────────────────────────────────

function ResultPanel({ result, activeTab, setActiveTab }) {
  const grouped = groupSteps(result.steps)
  const tabs = ["BCNF","UNION","4NF","5NF"].filter(g => grouped[g].length > 0)

  return (
    <section style={s.resultCard}>
      <div style={s.resHead}>
        <span style={s.resBadge}>✓ Dekompozicija završena</span>
        <span style={{fontSize:12,color:C.textMid}}>
          {result.relation_count} {result.relation_count===1?"šema":result.relation_count<5?"šeme":"šema"}
          {" · cilj: "}<strong style={{color:C.text}}>{result.target_nf}</strong>
        </span>
      </div>

      {/* Finalne relacije */}
      <div>
        <p style={s.blockLabel}>Rezultujuće šeme relacija</p>
        <div style={{display:"flex",flexDirection:"column",gap:10}}>
          {result.relations.map((rel,i) => <RelCard key={i} rel={rel} idx={i} />)}
        </div>
      </div>

      {/* Koraci */}
      <div>
        <p style={s.blockLabel}>Koraci dekompozicije</p>
        <div style={s.tabBar}>
          {tabs.map(tab => {
            const def = PHASE_GROUPS[tab]
            const active = activeTab === tab
            return (
              <button key={tab}
                style={{...s.tab, ...(active ? {
                  background:C.surface, borderColor:C.border,
                  borderBottomColor:"transparent", color:def.color
                } : {})}}
                onClick={() => setActiveTab(active ? null : tab)}>
                {def.label}
                <span style={{fontSize:11,fontWeight:700,padding:"1px 7px",borderRadius:10,
                  background: active ? def.color+"22" : C.surface,
                  color: active ? def.color : C.textDim}}>
                  {grouped[tab].length}
                </span>
              </button>
            )
          })}
        </div>
        {activeTab && grouped[activeTab]?.length > 0 && (
          <Timeline steps={grouped[activeTab]} color={PHASE_GROUPS[activeTab].color} />
        )}
      </div>
    </section>
  )
}

function RelCard({ rel, idx }) {
  const [open, setOpen] = useState(true)
  return (
    <div style={{background:C.surface,border:`1px solid ${C.border}`,borderRadius:10,overflow:"hidden"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",
        padding:"11px 16px",cursor:"pointer",borderBottom:open?`1px solid ${C.border}`:"none"}}
        onClick={() => setOpen(o=>!o)}>
        <div style={{display:"flex",alignItems:"baseline",gap:8}}>
          <span style={{fontSize:14,fontWeight:700,color:C.accent,letterSpacing:"0.04em"}}>
            R{idx+1}
          </span>
          <span style={{fontSize:13,color:C.text}}>({rel.attrs.join(", ")})</span>
        </div>
        <span style={{color:C.textDim,fontSize:11}}>{open?"▲":"▼"}</span>
      </div>
      {open && (
        <div style={{padding:"12px 16px",display:"flex",flexDirection:"column",gap:12}}>
          <div>
            <p style={s.miniLabel}>Kandidat {rel.candidate_keys.length===1?"ključ":"ključevi"}</p>
            <div style={{display:"flex",gap:6,flexWrap:"wrap",marginTop:4}}>
              {rel.candidate_keys.length===0
                ? <span style={{fontSize:12,color:C.textDim}}>—</span>
                : rel.candidate_keys.map((k,ki)=><Chip key={ki} v="key">{k.join(", ")}</Chip>)}
            </div>
          </div>
          {rel.fds.length > 0 && (
            <div>
              <p style={s.miniLabel}>Projektovane FZ</p>
              <div style={{display:"flex",flexDirection:"column",gap:5,marginTop:4}}>
                {rel.fds.map((fd,fi)=>(
                  <div key={fi} style={{display:"flex",alignItems:"center",gap:8}}>
                    <Chip v="lhs">{fd.lhs.join(", ")}</Chip>
                    <Arrow>→</Arrow>
                    <Chip v="rhs">{fd.rhs.join(", ")}</Chip>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function Timeline({ steps, color }) {
  const [expanded, setExpanded] = useState(() => new Set(steps.map((_,i)=>i)))

  function toggle(i) {
    setExpanded(prev => { const n=new Set(prev); n.has(i)?n.delete(i):n.add(i); return n })
  }

  const hasDetail = step =>
    step.relation || step.r1 || step.r2 || step.merged ||
    step.fd_lhs || step.mvd_lhs || step.jd_components ||
    step.component || step.components

  return (
    <div style={{display:"flex",flexDirection:"column",paddingLeft:6}}>
      {steps.map((step, i) => {
        const icon   = stepIcon(step.phase)
        const accent = stepAccentColor(step.phase, color)
        const detail = hasDetail(step)
        const isOpen = expanded.has(i)

        return (
          <div key={i} style={{display:"flex",gap:14,alignItems:"flex-start",
            position:"relative",paddingBottom:14}}>
            {i < steps.length-1 && (
              <div style={{position:"absolute",left:15,top:28,bottom:0,
                width:1,background:color+"33",zIndex:0}} />
            )}
            <div style={{width:30,height:30,borderRadius:"50%",flexShrink:0,zIndex:1,
              display:"flex",alignItems:"center",justifyContent:"center",
              background:accent+"18",border:`1.5px solid ${accent}`,
              color:accent,fontSize:11,fontWeight:700}}>
              {icon}
            </div>
            <div style={{flex:1,paddingTop:5,minWidth:0}}>
              <div style={{display:"flex",alignItems:"baseline",gap:6,flexWrap:"wrap",
                cursor:detail?"pointer":"default",userSelect:"none"}}
                onClick={()=>detail&&toggle(i)}>
                <span style={{fontSize:13,color:accent,lineHeight:1.5}}>{step.message}</span>
                {detail && (
                  <span style={{fontSize:11,color:C.textDim}}>
                    {isOpen?"▲ sklopi":"▼ detalji"}
                  </span>
                )}
              </div>

              {detail && isOpen && (
                <div style={{marginTop:8,background:C.bg,border:`1px solid ${C.border}`,
                  borderRadius:8,padding:"10px 14px",display:"flex",flexDirection:"column",gap:7}}>

                  {step.relation && (
                    <DRow label="Relacija"><ABox>{step.relation.join(", ")}</ABox></DRow>
                  )}
                  {step.fd_lhs && (
                    <DRow label="FZ">
                      <Chip v="lhs">{step.fd_lhs.join(", ")}</Chip>
                      <Arrow>→</Arrow>
                      <span style={{background:C.rhsBg,color:C.rhsText,padding:"3px 10px",
                        borderRadius:5,fontSize:13,fontWeight:600}}>{step.fd_rhs}</span>
                    </DRow>
                  )}
                  {step.mvd_lhs && (
                    <DRow label="MVD">
                      <Chip v="lhs">{step.mvd_lhs.join(", ")}</Chip>
                      <Arrow c={C.purple}>↠</Arrow>
                      <Chip v="rhs">{step.mvd_rhs.join(", ")}</Chip>
                    </DRow>
                  )}
                  {step.r1 && step.r2 && !step.merged && (
                    <DRow label="Podele">
                      <ABox>{step.r1.join(", ")}</ABox>
                      <span style={{color:C.textDim,fontSize:12}}>i</span>
                      <ABox>{step.r2.join(", ")}</ABox>
                    </DRow>
                  )}
                  {step.merged && (
                    <DRow label="Spojeno u"><ABox>{step.merged.join(", ")}</ABox></DRow>
                  )}
                  {step.jd_components && (
                    <DRow label="JD">
                      {step.jd_components.map((c,ci)=>(
                        <span key={ci} style={{display:"flex",alignItems:"center",gap:4}}>
                          <Chip v="amber">{c.join(", ")}</Chip>
                          {ci<step.jd_components.length-1&&<span style={{color:C.textDim}}>|</span>}
                        </span>
                      ))}
                    </DRow>
                  )}
                  {step.component && (
                    <DRow label="Komponenta"><ABox>{step.component.join(", ")}</ABox></DRow>
                  )}
                  {step.components && !step.jd_components && (
                    <DRow label="Podele">
                      {step.components.map((c,ci)=>(
                        <span key={ci} style={{display:"flex",alignItems:"center",gap:4}}>
                          <ABox>{c.join(", ")}</ABox>
                          {ci<step.components.length-1&&<span style={{color:C.textDim}}>·</span>}
                        </span>
                      ))}
                    </DRow>
                  )}
                </div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function DRow({ label, children }) {
  return (
    <div style={{display:"flex",gap:10,alignItems:"center",flexWrap:"wrap"}}>
      <span style={{fontSize:10,fontWeight:700,letterSpacing:"0.08em",color:C.textDim,
        textTransform:"uppercase",minWidth:68,flexShrink:0}}>{label}</span>
      <div style={{display:"flex",gap:6,alignItems:"center",flexWrap:"wrap"}}>{children}</div>
    </div>
  )
}

function ABox({ children }) {
  return (
    <span style={{background:C.border,color:C.text,padding:"2px 9px",
      borderRadius:4,fontSize:12,fontFamily:"inherit",letterSpacing:"0.04em"}}>
      {children}
    </span>
  )
}

// ── Stilovi ───────────────────────────────────────────────────────────────
const s = {
  page: {
    minHeight:"100vh", background:C.bg, display:"flex", justifyContent:"center",
    padding:"48px 16px 100px",
    fontFamily:"'IBM Plex Mono','Fira Code','Cascadia Code',monospace",
    color:C.text, position:"relative", overflowX:"hidden",
  },
  bgGlow1: {
    position:"fixed", top:-200, left:"15%", width:600, height:600, pointerEvents:"none", zIndex:0,
    background:`radial-gradient(circle, ${C.accentGlow} 0%, transparent 70%)`,
  },
  bgGlow2: {
    position:"fixed", bottom:-150, right:"5%", width:500, height:500, pointerEvents:"none", zIndex:0,
    background:`radial-gradient(circle, ${C.tealGlow} 0%, transparent 70%)`,
  },
  container: {
    width:"100%", maxWidth:760, display:"flex", flexDirection:"column",
    gap:20, position:"relative", zIndex:1,
  },
  header: {
    display:"flex", gap:16, alignItems:"flex-start", paddingLeft:4, marginBottom:4,
  },
  headerBar: {
    width:3, minHeight:52, flexShrink:0, marginTop:3, borderRadius:2,
    background:`linear-gradient(180deg, ${C.accent}, ${C.teal})`,
  },
  title: { fontSize:23, fontWeight:700, margin:"0 0 6px", letterSpacing:"-0.5px", color:C.text },
  subtitle: { fontSize:13, color:C.textMid, margin:0, lineHeight:1.65, maxWidth:520 },

  card: {
    background:C.card, border:`1px solid ${C.border}`,
    borderRadius:12, padding:"22px 26px", display:"flex", flexDirection:"column",
  },
  cardRow: { display:"flex", gap:16, flexWrap:"wrap", alignItems:"flex-end" },
  fieldCol: { display:"flex", flexDirection:"column", gap:8 },
  label: { fontSize:11, fontWeight:700, letterSpacing:"0.1em", color:C.accent, textTransform:"uppercase" },
  hint:  { fontWeight:400, textTransform:"none", letterSpacing:0, color:C.textDim, fontSize:11 },
  input: {
    background:C.surface, border:`1px solid ${C.border}`, borderRadius:8,
    padding:"9px 13px", fontSize:13, color:C.text, fontFamily:"inherit",
    outline:"none", width:"100%", boxSizing:"border-box",
  },
  nfGroup: { display:"flex", gap:8, marginTop:8 },
  nfBtn: {
    background:C.surface, border:`1px solid ${C.border}`, borderRadius:8,
    color:C.textMid, fontSize:13, fontWeight:600, fontFamily:"inherit",
    padding:"8px 20px", cursor:"pointer", letterSpacing:"0.04em",
  },
  nfActive: {
    background:C.accentDim, border:`1px solid ${C.accent}`, borderRadius:8,
    color:C.accent, fontSize:13, fontWeight:700, fontFamily:"inherit",
    padding:"8px 20px", cursor:"pointer", letterSpacing:"0.04em",
    boxShadow:`0 0 14px ${C.accentGlow}`,
  },
  sectionTitle: {
    fontSize:11, fontWeight:700, letterSpacing:"0.1em", color:C.accent,
    textTransform:"uppercase", margin:"0 0 14px",
  },
  secRow: { display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:14 },
  ifd: {
    background:C.surface, border:`1px solid ${C.border}`, borderRadius:8,
    padding:"8px 12px", fontSize:13, color:C.text, fontFamily:"inherit",
    outline:"none", flex:1, minWidth:0,
  },
  addRow: { display:"flex", gap:10, alignItems:"stretch" },
  actions: { display:"flex", gap:12, flexWrap:"wrap" },
  btnPrimary: {
    background:`linear-gradient(135deg, ${C.accent}, #3b7de8)`,
    border:"none", borderRadius:9, color:"#fff", fontSize:14, fontWeight:700,
    fontFamily:"inherit", padding:"12px 28px", cursor:"pointer", letterSpacing:"0.02em",
    boxShadow:`0 4px 20px ${C.accentGlow}`,
  },
  btnSec: {
    background:"transparent", border:`1px solid ${C.border}`, borderRadius:9,
    color:C.textMid, fontSize:13, fontFamily:"inherit", padding:"12px 20px", cursor:"pointer",
  },
  errBox: {
    background:C.errorBg, border:`1px solid ${C.errorBorder}`, borderRadius:9,
    color:C.error, fontSize:13, padding:"12px 16px", display:"flex", gap:10, alignItems:"flex-start",
  },
  resultCard: {
    background:C.card, border:`1px solid ${C.teal}44`, borderRadius:12,
    padding:"24px 26px", display:"flex", flexDirection:"column", gap:24,
  },
  resHead: { display:"flex", justifyContent:"space-between", alignItems:"center", flexWrap:"wrap", gap:10 },
  resBadge: {
    background:C.tealDim, color:C.teal, fontSize:11, fontWeight:700,
    letterSpacing:"0.1em", padding:"5px 14px", borderRadius:6, textTransform:"uppercase",
  },
  blockLabel: {
    fontSize:11, fontWeight:700, letterSpacing:"0.1em",
    color:C.textMid, textTransform:"uppercase", margin:"0 0 12px",
  },
  miniLabel: {
    fontSize:10, fontWeight:700, letterSpacing:"0.08em",
    color:C.textDim, textTransform:"uppercase", margin:0,
  },
  tabBar: {
    display:"flex", gap:6, flexWrap:"wrap", marginBottom:16,
    borderBottom:`1px solid ${C.border}`, paddingBottom:0,
  },
  tab: {
    background:"transparent", border:"1px solid transparent",
    borderBottom:"2px solid transparent", borderRadius:"8px 8px 0 0",
    color:C.textMid, fontSize:12, fontWeight:600, fontFamily:"inherit",
    padding:"8px 16px", cursor:"pointer", letterSpacing:"0.06em",
    display:"flex", alignItems:"center", gap:8, marginBottom:-1,
  },
}

const _style = document.createElement("style")
_style.textContent = `@keyframes spin { to { transform: rotate(360deg); } }`
document.head.appendChild(_style)