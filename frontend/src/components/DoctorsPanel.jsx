import { useState } from 'react';

export default function DoctorsPanel({ doctors, onAdd, onDelete }) {
  const [adding, setAdding] = useState(false);

  const submit = (e) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    onAdd({ name: form.get('name'), specialty: form.get('specialty'), room: form.get('room') });
    e.currentTarget.reset();
    setAdding(false);
  };

  return (
    <aside className="panel" id="doctors">
      <div className="panel-head">
        <div>
          <h2>Doctors</h2>
          <p className="muted">{doctors.length} on staff</p>
        </div>
        <button className="secondary" onClick={() => setAdding((v) => !v)}>{adding ? 'Close' : '＋ Add'}</button>
      </div>

      {adding && (
        <form className="inline-form" onSubmit={submit}>
          <input name="name" required minLength={2} placeholder="Dr. Full Name" />
          <input name="specialty" required minLength={2} placeholder="Specialty" />
          <input name="room" placeholder="Room" maxLength={20} />
          <button className="primary">Save doctor</button>
        </form>
      )}

      <ul className="doctor-list">
        {doctors.map((d) => (
          <li key={d.id}>
            <span className="avatar">{initials(d.name)}</span>
            <div>
              <b>{d.name}</b>
              <small>{d.specialty}{d.room ? ` · Room ${d.room}` : ''}</small>
            </div>
            <button className="ghost danger" title="Remove doctor" aria-label={`Remove ${d.name}`} onClick={() => onDelete(d)}>
              ✕
            </button>
          </li>
        ))}
        {!doctors.length && <li className="empty">No doctors yet.</li>}
      </ul>
    </aside>
  );
}

function initials(name) {
  return name
    .replace(/^Dr\.?\s*/i, '')
    .split(/\s+/)
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
}
