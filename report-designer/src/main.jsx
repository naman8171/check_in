import React from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const paletteItems = [
  { type: 'heading', label: 'Heading', icon: 'T', defaultContent: 'Monthly Sales Report' },
  { type: 'text', label: 'Text Block', icon: '¶', defaultContent: 'Write executive summary, insights, or notes here.' },
  { type: 'metric', label: 'Metric Card', icon: '↗', defaultContent: '$128.4K' },
  { type: 'chart', label: 'Chart', icon: '▥', defaultContent: 'Revenue Trend' },
  { type: 'table', label: 'Table', icon: '▦', defaultContent: 'Top Regions' },
  { type: 'signature', label: 'Signature', icon: '✍', defaultContent: 'Approved by Team Lead' },
]

const starterBlocks = [
  { id: 'block-1', type: 'heading', content: 'Q2 Performance Report', width: 'full', theme: 'indigo' },
  { id: 'block-2', type: 'metric', content: '$128.4K', width: 'half', theme: 'emerald' },
  { id: 'block-3', type: 'metric', content: '+24.8%', width: 'half', theme: 'violet' },
  { id: 'block-4', type: 'chart', content: 'Revenue Trend', width: 'full', theme: 'blue' },
  { id: 'block-5', type: 'text', content: 'Drag blocks from the left panel, reorder them inside the canvas, and customize the selected block from the right panel.', width: 'full', theme: 'slate' },
]

const themes = ['indigo', 'emerald', 'violet', 'blue', 'amber', 'rose', 'slate']
const widths = ['full', 'half']

function App() {
  const [blocks, setBlocks] = React.useState(starterBlocks)
  const [selectedId, setSelectedId] = React.useState(starterBlocks[0].id)
  const [isDraggingOverCanvas, setIsDraggingOverCanvas] = React.useState(false)
  const selectedBlock = blocks.find((block) => block.id === selectedId)

  const addBlock = (type, insertIndex = blocks.length) => {
    const palette = paletteItems.find((item) => item.type === type)
    const nextBlock = {
      id: `block-${crypto.randomUUID()}`,
      type,
      content: palette?.defaultContent ?? 'New report block',
      width: type === 'metric' ? 'half' : 'full',
      theme: themes[Math.floor(Math.random() * (themes.length - 1))],
    }

    setBlocks((current) => {
      const next = [...current]
      next.splice(insertIndex, 0, nextBlock)
      return next
    })
    setSelectedId(nextBlock.id)
  }

  const moveBlock = (dragId, targetId) => {
    if (!dragId || dragId === targetId) return
    setBlocks((current) => {
      const from = current.findIndex((block) => block.id === dragId)
      const to = current.findIndex((block) => block.id === targetId)
      if (from < 0 || to < 0) return current
      const next = [...current]
      const [moved] = next.splice(from, 1)
      next.splice(to, 0, moved)
      return next
    })
  }

  const updateSelected = (updates) => {
    setBlocks((current) => current.map((block) => (block.id === selectedId ? { ...block, ...updates } : block)))
  }

  const duplicateSelected = () => {
    if (!selectedBlock) return
    const clone = { ...selectedBlock, id: `block-${crypto.randomUUID()}`, content: `${selectedBlock.content} Copy` }
    const index = blocks.findIndex((block) => block.id === selectedBlock.id)
    setBlocks((current) => {
      const next = [...current]
      next.splice(index + 1, 0, clone)
      return next
    })
    setSelectedId(clone.id)
  }

  const deleteSelected = () => {
    setBlocks((current) => current.filter((block) => block.id !== selectedId))
    setSelectedId(blocks.find((block) => block.id !== selectedId)?.id ?? '')
  }

  const onCanvasDrop = (event) => {
    event.preventDefault()
    setIsDraggingOverCanvas(false)
    const type = event.dataTransfer.getData('component/type')
    if (type) addBlock(type)
  }

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">Drag & Drop Studio</p>
          <h1>Modern Report Designer</h1>
          <p>Components ko drag karo, canvas par drop karo, order change karo aur report ko polished dashboard jaisa design karo.</p>
        </div>
        <div className="hero-actions">
          <button type="button" onClick={() => window.print()}>Export / Print</button>
          <button type="button" className="ghost" onClick={() => { setBlocks(starterBlocks); setSelectedId(starterBlocks[0].id) }}>Reset</button>
        </div>
      </section>

      <section className="designer-grid">
        <aside className="panel palette-panel" aria-label="Component palette">
          <div className="panel-heading">
            <span>01</span>
            <h2>Blocks</h2>
          </div>
          <p className="muted">In cards ko drag karke report canvas me add karein.</p>
          <div className="palette-list">
            {paletteItems.map((item) => (
              <button
                className="palette-card"
                draggable
                key={item.type}
                type="button"
                onClick={() => addBlock(item.type)}
                onDragStart={(event) => event.dataTransfer.setData('component/type', item.type)}
              >
                <span>{item.icon}</span>
                <strong>{item.label}</strong>
              </button>
            ))}
          </div>
        </aside>

        <section
          className={`report-canvas ${isDraggingOverCanvas ? 'is-over' : ''}`}
          onDragOver={(event) => { event.preventDefault(); setIsDraggingOverCanvas(true) }}
          onDragLeave={() => setIsDraggingOverCanvas(false)}
          onDrop={onCanvasDrop}
        >
          <div className="paper-toolbar">
            <div>
              <span>Live Canvas</span>
              <strong>Annual Review.pdf</strong>
            </div>
            <small>{blocks.length} blocks</small>
          </div>
          <div className="paper">
            <div className="paper-header">
              <span>Confidential Report</span>
              <span>2026</span>
            </div>
            <div className="block-grid">
              {blocks.map((block) => (
                <ReportBlock
                  block={block}
                  isSelected={block.id === selectedId}
                  key={block.id}
                  onClick={() => setSelectedId(block.id)}
                  onMove={moveBlock}
                />
              ))}
            </div>
          </div>
        </section>

        <aside className="panel inspector-panel" aria-label="Block settings">
          <div className="panel-heading">
            <span>02</span>
            <h2>Customize</h2>
          </div>
          {selectedBlock ? (
            <div className="inspector-form">
              <label>
                Content
                <textarea value={selectedBlock.content} onChange={(event) => updateSelected({ content: event.target.value })} />
              </label>
              <label>
                Width
                <select value={selectedBlock.width} onChange={(event) => updateSelected({ width: event.target.value })}>
                  {widths.map((width) => <option key={width} value={width}>{width}</option>)}
                </select>
              </label>
              <label>
                Theme
                <select value={selectedBlock.theme} onChange={(event) => updateSelected({ theme: event.target.value })}>
                  {themes.map((theme) => <option key={theme} value={theme}>{theme}</option>)}
                </select>
              </label>
              <div className="button-row">
                <button type="button" onClick={duplicateSelected}>Duplicate</button>
                <button type="button" className="danger" onClick={deleteSelected}>Delete</button>
              </div>
            </div>
          ) : (
            <p className="muted">Canvas par koi block select karein.</p>
          )}
        </aside>
      </section>
    </main>
  )
}

function ReportBlock({ block, isSelected, onClick, onMove }) {
  return (
    <article
      className={`report-block ${block.width} ${block.theme} ${isSelected ? 'selected' : ''}`}
      draggable
      onClick={onClick}
      onDragStart={(event) => event.dataTransfer.setData('block/id', block.id)}
      onDragOver={(event) => event.preventDefault()}
      onDrop={(event) => {
        event.preventDefault()
        onMove(event.dataTransfer.getData('block/id'), block.id)
      }}
    >
      <div className="block-topline">
        <span>{block.type}</span>
        <span className="drag-handle">⋮⋮</span>
      </div>
      <BlockPreview block={block} />
    </article>
  )
}

function BlockPreview({ block }) {
  if (block.type === 'heading') return <h2>{block.content}</h2>
  if (block.type === 'text') return <p>{block.content}</p>
  if (block.type === 'metric') return <><strong className="metric-value">{block.content}</strong><span className="metric-label">Key metric</span></>
  if (block.type === 'chart') return <><h3>{block.content}</h3><div className="mini-chart"><span /><span /><span /><span /><span /></div></>
  if (block.type === 'table') return <><h3>{block.content}</h3><div className="mini-table"><span /><span /><span /><span /><span /><span /></div></>
  return <><h3>Signature</h3><p>{block.content}</p></>
}

createRoot(document.getElementById('root')).render(<App />)
