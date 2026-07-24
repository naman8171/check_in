import React, { useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

const money = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 })
const clampNumber = (value) => (Number.isFinite(Number(value)) ? Number(value) : 0)
const round = (value, digits = 2) => Number.parseFloat((Number.isFinite(value) ? value : 0).toFixed(digits))

const calculatorGroups = [
  {
    name: 'Finance',
    calculators: [
      { id: 'emi', title: 'EMI Calculator', desc: 'Monthly loan EMI with interest and total payable.' },
      { id: 'sip', title: 'SIP Calculator', desc: 'Future value for monthly investments.' },
      { id: 'gst', title: 'GST Calculator', desc: 'Add or remove GST without duplicate tax math.' },
      { id: 'discount', title: 'Discount Calculator', desc: 'Final price and savings after a percentage discount.' },
    ],
  },
  {
    name: 'Health',
    calculators: [
      { id: 'bmi', title: 'BMI Calculator', desc: 'Body mass index with an instant category.' },
      { id: 'calorie', title: 'Calorie Calculator', desc: 'BMR and daily maintenance calories.' },
    ],
  },
  {
    name: 'Everyday',
    calculators: [
      { id: 'age', title: 'Age Calculator', desc: 'Exact age from your birth date.' },
      { id: 'percentage', title: 'Percentage Calculator', desc: 'Find percent value, percentage, or change.' },
      { id: 'unit', title: 'Unit Converter', desc: 'Length, weight, temperature, and area conversions.' },
    ],
  },
]

const flatCalculators = calculatorGroups.flatMap((group) => group.calculators.map((calculator) => ({ ...calculator, group: group.name })))
const defaultValues = {
  emi: { amount: 500000, rate: 9, years: 5 },
  sip: { monthly: 5000, rate: 12, years: 10 },
  gst: { amount: 1000, rate: 18, mode: 'add' },
  discount: { price: 2499, discount: 20 },
  bmi: { weight: 70, height: 170 },
  calorie: { gender: 'male', age: 28, weight: 70, height: 170, activity: 1.375 },
  age: { dob: '2000-01-01' },
  percentage: { mode: 'percentOf', value: 20, total: 500, from: 100, to: 125 },
  unit: { type: 'length', value: 1, from: 'km', to: 'm' },
}

const unitTypes = {
  length: { label: 'Length', units: { mm: 0.001, cm: 0.01, m: 1, km: 1000, in: 0.0254, ft: 0.3048, yd: 0.9144, mi: 1609.344 } },
  weight: { label: 'Weight', units: { mg: 0.000001, g: 0.001, kg: 1, lb: 0.45359237, oz: 0.0283495231 } },
  area: { label: 'Area', units: { 'sq m': 1, 'sq ft': 0.09290304, acre: 4046.8564224, hectare: 10000 } },
  temperature: { label: 'Temperature', units: { celsius: 'celsius', fahrenheit: 'fahrenheit', kelvin: 'kelvin' } },
}

function App() {
  const [activeId, setActiveId] = useState('emi')
  const [search, setSearch] = useState('')
  const [values, setValues] = useState(defaultValues)
  const activeCalculator = flatCalculators.find((calculator) => calculator.id === activeId) ?? flatCalculators[0]
  const visibleGroups = calculatorGroups.map((group) => ({
    ...group,
    calculators: group.calculators.filter((calculator) => `${calculator.title} ${calculator.desc}`.toLowerCase().includes(search.toLowerCase().trim())),
  })).filter((group) => group.calculators.length)

  const update = (id, field, value) => setValues((current) => ({ ...current, [id]: { ...current[id], [field]: value } }))

  return (
    <main className="app-shell">
      <section className="hero-card">
        <div>
          <p className="eyebrow">AllIn1Calculator • React JS</p>
          <h1>Clean, fixed and duplicate-free calculators.</h1>
          <p className="hero-copy">Finance, health, percentage, age and unit tools in one responsive dashboard with guarded formulas, clear outputs and polished UI.</p>
        </div>
        <div className="hero-stats">
          <span><strong>{flatCalculators.length}</strong> calculators</span>
          <span><strong>{calculatorGroups.length}</strong> categories</span>
          <span><strong>0</strong> duplicate cards</span>
        </div>
      </section>

      <section className="workspace">
        <aside className="sidebar" aria-label="Calculator list">
          <label className="search-box">
            <span>Search calculator</span>
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="EMI, BMI, GST..." />
          </label>
          {visibleGroups.map((group) => (
            <div className="nav-group" key={group.name}>
              <h2>{group.name}</h2>
              {group.calculators.map((calculator) => (
                <button key={calculator.id} className={activeId === calculator.id ? 'active' : ''} type="button" onClick={() => setActiveId(calculator.id)}>
                  <strong>{calculator.title}</strong>
                  <small>{calculator.desc}</small>
                </button>
              ))}
            </div>
          ))}
        </aside>
        <CalculatorPanel calculator={activeCalculator} values={values[activeCalculator.id]} update={(field, value) => update(activeCalculator.id, field, value)} />
      </section>
    </main>
  )
}

function CalculatorPanel({ calculator, values, update }) {
  const result = useMemo(() => calculate(calculator.id, values), [calculator.id, values])
  return <section className="calculator-panel"><p className="panel-kicker">{calculator.group}</p><h2>{calculator.title}</h2><p>{calculator.desc}</p><Form id={calculator.id} values={values} update={update} /><Result result={result} /></section>
}

function Field({ label, type = 'number', value, onChange, ...props }) {
  return <label className="field"><span>{label}</span><input type={type} value={value} onChange={(event) => onChange(event.target.value)} {...props} /></label>
}
function Select({ label, value, onChange, children }) { return <label className="field"><span>{label}</span><select value={value} onChange={(event) => onChange(event.target.value)}>{children}</select></label> }

function Form({ id, values, update }) {
  if (id === 'emi') return <div className="form-grid"><Field label="Loan amount" value={values.amount} onChange={(v) => update('amount', v)} /><Field label="Interest % p.a." value={values.rate} onChange={(v) => update('rate', v)} /><Field label="Tenure years" value={values.years} onChange={(v) => update('years', v)} /></div>
  if (id === 'sip') return <div className="form-grid"><Field label="Monthly SIP" value={values.monthly} onChange={(v) => update('monthly', v)} /><Field label="Return % p.a." value={values.rate} onChange={(v) => update('rate', v)} /><Field label="Years" value={values.years} onChange={(v) => update('years', v)} /></div>
  if (id === 'gst') return <div className="form-grid"><Field label="Amount" value={values.amount} onChange={(v) => update('amount', v)} /><Field label="GST %" value={values.rate} onChange={(v) => update('rate', v)} /><Select label="Mode" value={values.mode} onChange={(v) => update('mode', v)}><option value="add">Add GST</option><option value="remove">Remove GST</option></Select></div>
  if (id === 'discount') return <div className="form-grid"><Field label="Original price" value={values.price} onChange={(v) => update('price', v)} /><Field label="Discount %" value={values.discount} onChange={(v) => update('discount', v)} /></div>
  if (id === 'bmi') return <div className="form-grid"><Field label="Weight kg" value={values.weight} onChange={(v) => update('weight', v)} /><Field label="Height cm" value={values.height} onChange={(v) => update('height', v)} /></div>
  if (id === 'calorie') return <div className="form-grid"><Select label="Gender" value={values.gender} onChange={(v) => update('gender', v)}><option value="male">Male</option><option value="female">Female</option></Select><Field label="Age" value={values.age} onChange={(v) => update('age', v)} /><Field label="Weight kg" value={values.weight} onChange={(v) => update('weight', v)} /><Field label="Height cm" value={values.height} onChange={(v) => update('height', v)} /><Select label="Activity" value={values.activity} onChange={(v) => update('activity', v)}><option value="1.2">Sedentary</option><option value="1.375">Light</option><option value="1.55">Moderate</option><option value="1.725">Active</option></Select></div>
  if (id === 'age') return <div className="form-grid"><Field label="Date of birth" type="date" value={values.dob} onChange={(v) => update('dob', v)} /></div>
  if (id === 'percentage') return <div className="form-grid"><Select label="Calculation" value={values.mode} onChange={(v) => update('mode', v)}><option value="percentOf">X% of Y</option><option value="whatPercent">X is what % of Y</option><option value="change">% change from X to Y</option></Select><Field label="Value / from" value={values.value} onChange={(v) => update('value', v)} /><Field label="Total / to" value={values.total} onChange={(v) => update('total', v)} /></div>
  return <div className="form-grid"><Select label="Type" value={values.type} onChange={(v) => { const units = Object.keys(unitTypes[v].units); update('type', v); update('from', units[0]); update('to', units[1] ?? units[0]); }}>{Object.entries(unitTypes).map(([key, type]) => <option key={key} value={key}>{type.label}</option>)}</Select><Field label="Value" value={values.value} onChange={(v) => update('value', v)} /><Select label="From" value={values.from} onChange={(v) => update('from', v)}>{Object.keys(unitTypes[values.type].units).map((unit) => <option key={unit}>{unit}</option>)}</Select><Select label="To" value={values.to} onChange={(v) => update('to', v)}>{Object.keys(unitTypes[values.type].units).map((unit) => <option key={unit}>{unit}</option>)}</Select></div>
}

function Result({ result }) { return <div className="result-card"><span>{result.label}</span><strong>{result.primary}</strong>{result.rows.map((row) => <p key={row.name}><span>{row.name}</span><b>{row.value}</b></p>)}</div> }

function calculate(id, values) {
  if (id === 'emi') { const p = clampNumber(values.amount), r = clampNumber(values.rate) / 1200, n = clampNumber(values.years) * 12; const emi = r && n ? p * r * ((1 + r) ** n) / (((1 + r) ** n) - 1) : p / Math.max(n, 1); return { label: 'Monthly EMI', primary: `₹${money.format(round(emi))}`, rows: [{ name: 'Total interest', value: `₹${money.format(round(emi * n - p))}` }, { name: 'Total payable', value: `₹${money.format(round(emi * n))}` }] } }
  if (id === 'sip') { const m = clampNumber(values.monthly), r = clampNumber(values.rate) / 1200, n = clampNumber(values.years) * 12; const future = r && n ? m * (((1 + r) ** n - 1) / r) * (1 + r) : m * n; return { label: 'Future value', primary: `₹${money.format(round(future))}`, rows: [{ name: 'Invested amount', value: `₹${money.format(round(m * n))}` }, { name: 'Estimated gain', value: `₹${money.format(round(future - m * n))}` }] } }
  if (id === 'gst') { const a = clampNumber(values.amount), r = clampNumber(values.rate) / 100; const tax = values.mode === 'remove' ? a - a / (1 + r) : a * r; const total = values.mode === 'remove' ? a - tax : a + tax; return { label: values.mode === 'remove' ? 'Base amount' : 'Total amount', primary: `₹${money.format(round(total))}`, rows: [{ name: 'GST amount', value: `₹${money.format(round(tax))}` }, { name: 'Rate', value: `${values.rate}%` }] } }
  if (id === 'discount') { const price = clampNumber(values.price), savings = price * clampNumber(values.discount) / 100; return { label: 'Final price', primary: `₹${money.format(round(price - savings))}`, rows: [{ name: 'You save', value: `₹${money.format(round(savings))}` }] } }
  if (id === 'bmi') { const bmi = clampNumber(values.weight) / ((clampNumber(values.height) / 100) ** 2); const category = bmi < 18.5 ? 'Underweight' : bmi < 25 ? 'Healthy' : bmi < 30 ? 'Overweight' : 'Obese'; return { label: 'BMI score', primary: round(bmi, 1), rows: [{ name: 'Category', value: category }] } }
  if (id === 'calorie') { const base = 10 * clampNumber(values.weight) + 6.25 * clampNumber(values.height) - 5 * clampNumber(values.age) + (values.gender === 'male' ? 5 : -161); const daily = base * clampNumber(values.activity); return { label: 'Maintenance calories', primary: `${money.format(round(daily, 0))} kcal`, rows: [{ name: 'BMR', value: `${money.format(round(base, 0))} kcal` }] } }
  if (id === 'age') { const birth = new Date(values.dob), today = new Date(); let years = today.getFullYear() - birth.getFullYear(); const hadBirthday = today.getMonth() > birth.getMonth() || (today.getMonth() === birth.getMonth() && today.getDate() >= birth.getDate()); if (!hadBirthday) years -= 1; return { label: 'Age', primary: `${Math.max(years, 0)} years`, rows: [{ name: 'Birth date', value: values.dob || 'Select a date' }] } }
  if (id === 'percentage') { const x = clampNumber(values.value), y = clampNumber(values.total); const answer = values.mode === 'percentOf' ? x * y / 100 : values.mode === 'whatPercent' ? x / Math.max(y, 1) * 100 : (y - x) / Math.max(Math.abs(x), 1) * 100; return { label: 'Answer', primary: values.mode === 'percentOf' ? round(answer) : `${round(answer)}%`, rows: [{ name: 'Formula', value: values.mode === 'percentOf' ? 'X × Y ÷ 100' : values.mode === 'whatPercent' ? 'X ÷ Y × 100' : '(Y - X) ÷ X × 100' }] } }
  return convertUnit(values)
}

function convertTemperature(value, from, to) { const c = from === 'celsius' ? value : from === 'fahrenheit' ? (value - 32) * 5 / 9 : value - 273.15; return to === 'celsius' ? c : to === 'fahrenheit' ? (c * 9 / 5) + 32 : c + 273.15 }
function convertUnit(values) { const type = unitTypes[values.type] ?? unitTypes.length; const value = clampNumber(values.value); const converted = values.type === 'temperature' ? convertTemperature(value, values.from, values.to) : value * type.units[values.from] / type.units[values.to]; return { label: 'Converted value', primary: `${round(converted, 4)} ${values.to}`, rows: [{ name: 'From', value: `${value} ${values.from}` }] } }

createRoot(document.getElementById('root')).render(<App />)
