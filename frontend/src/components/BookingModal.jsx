import { useState } from 'react';
import { api } from '../api.js';

function defaultSlot() {
  // Next half-hour from now, in local time.
  const d = new Date();
  d.setMinutes(d.getMinutes() < 30 ? 30 : 60, 0, 0);
  const pad = (n) => String(n).padStart(2, '0');
  return {
    date: `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`,
    time: `${pad(d.getHours())}:${pad(d.getMinutes())}`,
  };
}

export default function BookingModal({ doctors, onClose, onBooked }) {
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const slot = defaultSlot();

  const submit = async (e) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    setSaving(true);
    setError('');
    try {
      const appt = await api.createAppointment({
        patient_name: f.get('patient_name'),
        patient_phone: f.get('patient_phone'),
        doctor_id: Number(f.get('doctor_id')),
        scheduled_at: new Date(`${f.get('date')}T${f.get('time')}`).toISOString(),
        duration_minutes: Number(f.get('duration_minutes')),
        reason: f.get('reason'),
      });
      onBooked(appt);
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <form className="modal" onSubmit={submit}>
        <div className="modal-head">
          <div>
            <p className="eyebrow">New booking</p>
            <h2>Book an appointment</h2>
          </div>
          <button type="button" className="close" aria-label="Close" onClick={onClose}>×</button>
        </div>

        {error && <div className="alert" role="alert">⚠ {error}</div>}

        <div className="form-row">
          <label>Patient name<input name="patient_name" required minLength={2} placeholder="e.g. Asha Verma" /></label>
          <label>Phone<input name="patient_phone" type="tel" maxLength={20} placeholder="98765 43210" /></label>
        </div>
        <label>
          Doctor
          <select name="doctor_id" required>
            {doctors.map((d) => (
              <option key={d.id} value={d.id}>{d.name} — {d.specialty}</option>
            ))}
          </select>
        </label>
        <div className="form-row three">
          <label>Date<input name="date" type="date" required defaultValue={slot.date} /></label>
          <label>Time<input name="time" type="time" required step={900} defaultValue={slot.time} /></label>
          <label>
            Duration
            <select name="duration_minutes" defaultValue="30">
              <option value="15">15 min</option>
              <option value="30">30 min</option>
              <option value="45">45 min</option>
              <option value="60">60 min</option>
            </select>
          </label>
        </div>
        <label>Reason for visit<textarea name="reason" placeholder="Symptoms, follow-up, check-up…" /></label>
        <button className="primary full" disabled={saving}>{saving ? 'Booking…' : 'Confirm booking'}</button>
      </form>
    </div>
  );
}
