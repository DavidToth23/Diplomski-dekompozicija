import { useState } from "react"

const API = "http://localhost:8000/api"

// Inicijalni primer (R, AB→C, C→D, D→E)
const EXAMPLE = {
  relation_name: "R",
  attributes: ["A", "B", "C", "D", "E"],
  functional_dependencies: [
    { lhs: ["A", "B"], rhs: ["C"] },
    { lhs: ["C"],      rhs: ["D"] },
    { lhs: ["D"],      rhs: ["E"] },
  ],
}

export default function App() {
  const [relationName, setRelationName]   = useState(EXAMPLE.relation_name)
  const [attrsInput, setAttrsInput]       = useState(EXAMPLE.attributes.join(", "))
  const [fds, setFds]                     = useState(EXAMPLE.functional_dependencies)
  const [lhsInput, setLhsInput]           = useState("")
  const [rhsInput, setRhsInput]           = useState("")
  const [result, setResult]               = useState(null)
  const [error, setError]                 = useState(null)
  const [loading, setLoading]             = useState(false)

  // ── Dodaj FZ ───────────────────────────────────────────────────────────────
  function addFd() {
    const lhs = lhsInput.split(",").map(s => s.trim().toUpperCase()).filter(Boolean)
    const rhs = rhsInput.split(",").map(s => s.trim().toUpperCase()).filter(Boolean)
    if (!lhs.length || !rhs.length) return
    setFds(prev => [...prev, { lhs, rhs }])
    setLhsInput("")
    setRhsInput("")
  }

  // ── Ukloni FZ ──────────────────────────────────────────────────────────────
  function removeFd(index) {
    setFds(prev => prev.filter((_, i) => i !== index))
  }

  // ── Pošalji na backend ─────────────────────────────────────────────────────
  async function handleSubmit() {
    setError(null)
    setResult(null)
    setLoading(true)

    const attributes = attrsInput
      .split(",")
      .map(s => s.trim().toUpperCase())
      .filter(Boolean)

    const payload = {
      relation_name: relationName.toUpperCase(),
      attributes,
      functional_dependencies: fds,
    }

    try {
      const res = await fetch(`${API}/schema`, {
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
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  // ── Resetuj ────────────────────────────────────────────────────────────────
  function handleReset() {
    setRelationName(EXAMPLE.relation_name)
    setAttrsInput(EXAMPLE.attributes.join(", "))
    setFds(EXAMPLE.functional_dependencies)
    setResult(null)
    setError(null)
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div style={styles.page}>
      <div style={styles.container}>

        {/* ── Header ── */}
        <header style={styles.header}>
          <div style={styles.headerAccent} />
          <h1 style={styles.title}>Dekompozicija šeme relacije</h1>
          <p style={styles.subtitle}>
            Unesi skup obeležja i funkcionalne zavisnosti — alat će prikazati
            korake dekompozicije.
          </p>
        </header>

        {/* ── Ime relacije + obelezja ── */}
        <section style={styles.card}>
          <label style={styles.label}>Ime relacije</label>
          <input
            style={styles.inputSmall}
            value={relationName}
            onChange={e => setRelationName(e.target.value)}
            placeholder="npr. R"
            maxLength={10}
          />

          <label style={{ ...styles.label, marginTop: 20 }}>
            Skup obeležja{" "}
            <span style={styles.hint}>(odvojeni zarezom)</span>
          </label>
          <input
            style={styles.input}
            value={attrsInput}
            onChange={e => setAttrsInput(e.target.value)}
            placeholder="npr. A, B, C, D, E"
          />
        </section>

        {/* ── Unos FZ-ova ── */}
        <section style={styles.card}>
          <p style={styles.sectionTitle}>Funkcionalne zavisnosti</p>

          {/* Lista postojecih FZ-ova */}
          <div style={styles.fdList}>
            {fds.length === 0 && (
              <p style={styles.emptyMsg}>Još nema unetih zavisnosti.</p>
            )}
            {fds.map((fd, i) => (
              <div key={i} style={styles.fdRow}>
                <span style={styles.fdBadgeLhs}>
                  {fd.lhs.join(", ")}
                </span>
                <span style={styles.fdArrow}>→</span>
                <span style={styles.fdBadgeRhs}>
                  {fd.rhs.join(", ")}
                </span>
                <button
                  style={styles.removeBtn}
                  onClick={() => removeFd(i)}
                  title="Ukloni ovu zavisnost"
                >
                  ×
                </button>
              </div>
            ))}
          </div>

          {/* Forma za novu FZ */}
          <div style={styles.addFdRow}>
            <div style={styles.fdInputGroup}>
              <input
                style={styles.inputFd}
                value={lhsInput}
                onChange={e => setLhsInput(e.target.value)}
                placeholder="Leva strana  (npr. A, B)"
                onKeyDown={e => e.key === "Enter" && addFd()}
              />
              <span style={styles.fdArrowAdd}>→</span>
              <input
                style={styles.inputFd}
                value={rhsInput}
                onChange={e => setRhsInput(e.target.value)}
                placeholder="Desna strana  (npr. C)"
                onKeyDown={e => e.key === "Enter" && addFd()}
              />
            </div>
            <button style={styles.addBtn} onClick={addFd}>
              + Dodaj
            </button>
          </div>
        </section>

        {/* ── Akcioni dugmici ── */}
        <div style={styles.actions}>
          <button style={styles.btnPrimary} onClick={handleSubmit} disabled={loading}>
            {loading ? "Obrađujem..." : "Pošalji na server →"}
          </button>
          <button style={styles.btnSecondary} onClick={handleReset}>
            Resetuj na primer
          </button>
        </div>

        {/* ── Greska ── */}
        {error && (
          <div style={styles.errorBox}>
            <strong>Greška:</strong> {error}
          </div>
        )}

        {/* ── Rezultat sa servera ── */}
        {result && <ResultPanel result={result} />}

      </div>
    </div>
  )
}

// Komponenta za prikaz odgovora sa servera
function ResultPanel({ result }) {
  return (
    <section style={styles.resultCard}>
      <div style={styles.resultHeader}>
        <span style={styles.resultBadge}>✓ Odgovor sa servera</span>
      </div>

      <p style={styles.summaryText}>{result.summary}</p>

      {/* Obelezja */}
      <div style={styles.resultBlock}>
        <p style={styles.resultLabel}>
          Relacija{" "}
          <strong>{result.relation_name}</strong> — skup obeležja
        </p>
        <div style={styles.attrRow}>
          {result.attributes.map(a => (
            <span key={a} style={styles.attrChip}>{a}</span>
          ))}
        </div>
      </div>

      {/* Funkcionalne zavisnosti */}
      <div style={styles.resultBlock}>
        <p style={styles.resultLabel}>Funkcionalne zavisnosti (normalizovane)</p>
        {result.functional_dependencies.map((fd, i) => (
          <div key={i} style={styles.resultFdRow}>
            <span style={styles.stepNum}>{i + 1}</span>
            <code style={styles.fdCode}>{fd.display}</code>
          </div>
        ))}
      </div>

      {/* Sirovi JSON */}
      <details style={styles.jsonDetails}>
        <summary style={styles.jsonSummary}>Prikaži sirovi JSON odgovor</summary>
        <pre style={styles.jsonPre}>{JSON.stringify(result, null, 2)}</pre>
      </details>
    </section>
  )
}

// Stilovi
const C = {
  bg:       "#0f1117",
  surface:  "#181c27",
  card:     "#1e2333",
  border:   "#2a3050",
  accent:   "#4f8ef7",
  accentDim:"#2a4a8a",
  text:     "#e8eaf6",
  textMid:  "#8b93b5",
  textDim:  "#5a6280",
  lhs:      "#3b5bdb",
  lhsBg:    "#1a2a5e",
  rhs:      "#0ca678",
  rhsBg:    "#0a3528",
  success:  "#0ca678",
  successBg:"#072820",
  error:    "#f03e3e",
  errorBg:  "#3b1111",
}

const styles = {
  page: {
    minHeight: "100vh",
    background: C.bg,
    display: "flex",
    justifyContent: "center",
    padding: "48px 16px 80px",
    fontFamily: "'IBM Plex Mono', 'Fira Code', monospace",
    color: C.text,
  },
  container: {
    width: "100%",
    maxWidth: 720,
    display: "flex",
    flexDirection: "column",
    gap: 24,
  },
  header: {
    position: "relative",
    paddingLeft: 20,
    marginBottom: 8,
  },
  headerAccent: {
    position: "absolute",
    left: 0, top: 0, bottom: 0,
    width: 3,
    background: C.accent,
    borderRadius: 2,
  },
  title: {
    fontSize: 26,
    fontWeight: 600,
    margin: "0 0 8px",
    letterSpacing: "-0.5px",
    color: C.text,
  },
  subtitle: {
    fontSize: 14,
    color: C.textMid,
    margin: 0,
    lineHeight: 1.6,
  },
  card: {
    background: C.card,
    border: `1px solid ${C.border}`,
    borderRadius: 12,
    padding: "24px 28px",
    display: "flex",
    flexDirection: "column",
  },
  label: {
    fontSize: 12,
    fontWeight: 600,
    letterSpacing: "0.08em",
    color: C.accent,
    textTransform: "uppercase",
    marginBottom: 8,
  },
  hint: {
    fontWeight: 400,
    textTransform: "none",
    letterSpacing: 0,
    color: C.textDim,
    fontSize: 11,
  },
  input: {
    background: C.surface,
    border: `1px solid ${C.border}`,
    borderRadius: 8,
    padding: "10px 14px",
    fontSize: 14,
    color: C.text,
    fontFamily: "inherit",
    outline: "none",
    width: "100%",
    boxSizing: "border-box",
  },
  inputSmall: {
    background: C.surface,
    border: `1px solid ${C.border}`,
    borderRadius: 8,
    padding: "10px 14px",
    fontSize: 14,
    color: C.text,
    fontFamily: "inherit",
    outline: "none",
    width: 120,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: 600,
    letterSpacing: "0.08em",
    color: C.accent,
    textTransform: "uppercase",
    margin: "0 0 16px",
  },
  fdList: {
    display: "flex",
    flexDirection: "column",
    gap: 8,
    marginBottom: 20,
    minHeight: 40,
  },
  emptyMsg: {
    fontSize: 13,
    color: C.textDim,
    margin: 0,
    fontStyle: "italic",
  },
  fdRow: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    background: C.surface,
    border: `1px solid ${C.border}`,
    borderRadius: 8,
    padding: "8px 14px",
  },
  fdBadgeLhs: {
    background: C.lhsBg,
    color: "#7aa2ff",
    padding: "3px 10px",
    borderRadius: 5,
    fontSize: 13,
    fontWeight: 600,
    letterSpacing: "0.05em",
  },
  fdArrow: {
    color: C.textMid,
    fontSize: 16,
  },
  fdBadgeRhs: {
    background: C.rhsBg,
    color: "#3ecfa0",
    padding: "3px 10px",
    borderRadius: 5,
    fontSize: 13,
    fontWeight: 600,
    letterSpacing: "0.05em",
    flex: 1,
  },
  removeBtn: {
    background: "transparent",
    border: "none",
    color: C.textDim,
    fontSize: 18,
    cursor: "pointer",
    padding: "0 4px",
    lineHeight: 1,
    borderRadius: 4,
  },
  addFdRow: {
    display: "flex",
    gap: 10,
    alignItems: "stretch",
    flexWrap: "wrap",
  },
  fdInputGroup: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    flex: 1,
    minWidth: 260,
  },
  inputFd: {
    background: C.surface,
    border: `1px solid ${C.border}`,
    borderRadius: 8,
    padding: "9px 12px",
    fontSize: 13,
    color: C.text,
    fontFamily: "inherit",
    outline: "none",
    flex: 1,
    minWidth: 0,
  },
  fdArrowAdd: {
    color: C.textMid,
    fontSize: 18,
    flexShrink: 0,
  },
  addBtn: {
    background: C.accentDim,
    border: `1px solid ${C.accent}`,
    borderRadius: 8,
    color: C.accent,
    fontSize: 13,
    fontWeight: 600,
    fontFamily: "inherit",
    padding: "9px 18px",
    cursor: "pointer",
    whiteSpace: "nowrap",
    letterSpacing: "0.03em",
  },
  actions: {
    display: "flex",
    gap: 12,
    flexWrap: "wrap",
  },
  btnPrimary: {
    background: C.accent,
    border: "none",
    borderRadius: 8,
    color: "#fff",
    fontSize: 14,
    fontWeight: 600,
    fontFamily: "inherit",
    padding: "12px 24px",
    cursor: "pointer",
    letterSpacing: "0.02em",
  },
  btnSecondary: {
    background: "transparent",
    border: `1px solid ${C.border}`,
    borderRadius: 8,
    color: C.textMid,
    fontSize: 14,
    fontFamily: "inherit",
    padding: "12px 20px",
    cursor: "pointer",
  },
  errorBox: {
    background: C.errorBg,
    border: `1px solid ${C.error}`,
    borderRadius: 8,
    color: "#ff8080",
    fontSize: 13,
    padding: "14px 18px",
  },
  // ── Rezultat ──
  resultCard: {
    background: C.card,
    border: `1px solid ${C.success}44`,
    borderRadius: 12,
    padding: "24px 28px",
    display: "flex",
    flexDirection: "column",
    gap: 20,
  },
  resultHeader: {
    display: "flex",
    alignItems: "center",
  },
  resultBadge: {
    background: C.successBg,
    color: C.success,
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: "0.08em",
    padding: "4px 12px",
    borderRadius: 5,
    textTransform: "uppercase",
  },
  summaryText: {
    fontSize: 15,
    color: C.text,
    margin: 0,
    lineHeight: 1.6,
    borderLeft: `3px solid ${C.accent}`,
    paddingLeft: 14,
  },
  resultBlock: {
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
  resultLabel: {
    fontSize: 12,
    color: C.textMid,
    margin: 0,
    letterSpacing: "0.04em",
  },
  attrRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: 8,
  },
  attrChip: {
    background: C.lhsBg,
    color: "#7aa2ff",
    padding: "5px 14px",
    borderRadius: 6,
    fontSize: 14,
    fontWeight: 700,
    letterSpacing: "0.06em",
  },
  resultFdRow: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    padding: "6px 0",
    borderBottom: `1px solid ${C.border}`,
  },
  stepNum: {
    fontSize: 11,
    color: C.textDim,
    minWidth: 18,
  },
  fdCode: {
    fontSize: 14,
    color: C.text,
    fontFamily: "inherit",
    letterSpacing: "0.04em",
  },
  jsonDetails: {
    marginTop: 4,
  },
  jsonSummary: {
    fontSize: 12,
    color: C.textDim,
    cursor: "pointer",
    letterSpacing: "0.04em",
  },
  jsonPre: {
    background: C.surface,
    border: `1px solid ${C.border}`,
    borderRadius: 8,
    padding: 16,
    fontSize: 12,
    color: C.textMid,
    overflowX: "auto",
    marginTop: 10,
    lineHeight: 1.7,
    fontFamily: "inherit",
  },
}