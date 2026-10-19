import { useCallback, useEffect, useState } from 'react';
import { api } from './api.js';
import BookingModal from './components/BookingModal.jsx';
import DoctorsPanel from './components/DoctorsPanel.jsx';
import AppointmentsTable from './components/AppointmentsTable.jsx';

const EMPTY_STATS = { total: 0, today: 0, scheduled: 0, checkedIn: 0, completed: 0, cancelled: 0, doctors: 0 };

export default function App() {
  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [stats, setStats] = useState(EMPTY_STATS);
  const [filters, setFilters] = useState({ status: '', doctor_id: '', on: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');
  const [showBooking, setShowBooking] = useState(false);

  const load = useCallback(async () => {
    try {
      const [docs, appts, summary] = await Promise.all([
        api.listDoctors(),
        api.listAppointments(filters),
        api.stats(),
      ]);
      setDoctors(docs);
      setAppointments(appts);
      setStats(summary);
      setError('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!toast) return undefined;
    const timer = setTimeout(() => setToast(''), 3500);
    return () => clearTimeout(timer);
  }, [toast]);

  // Wraps a mutation so failures surface as a toast and data is refreshed afterwards.
  const run = async (action, successMessage) => {
    try {
      await action();
      if (successMessage) setToast(successMessage);
    } catch (e) {
      setToast(`⚠ ${e.message}`);
    }
    load();
  };

  const today = new Date().toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long' });

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">✚</span>
          <div>
            <b>ClinicFlow</b>
            <small>Front-desk console</small>
          </div>
        </div>
        <nav>
          <a href="#overview" className="active">◧ <span>Overview</span></a>
          <a href="#appointments">◷ <span>Appointments</span></a>
          <a href="#doctors">⚕ <span>Doctors</span></a>
        </nav>
        <div className="side-bottom">
          <div className="pipeline-card">
            <strong>Delivery pipeline</strong>
            <div className="pipeline">
              <span>Test</span><i /><span>Build</span><i /><span>Scan</span><i /><span>Deploy</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="main" id="overview">
        <header className="page-head">
          <div>
            <p className="eyebrow">{today}</p>
            <h1>Clinic overview, live demo</h1>
            <p className="muted">Book, check in and close out patient visits.</p>
          </div>
          <button className="primary" onClick={() => setShowBooking(true)} disabled={!doctors.length}>
            ＋ Book appointment
          </button>
        </header>

        {error && (
          <div className="alert" role="alert">
            ⚠ {error}. Make sure the backend and PostgreSQL are running, then refresh.
          </div>
        )}

        <section className="stats">
          <Stat label="Today" value={stats.today} tone="teal" />
          <Stat label="Scheduled" value={stats.scheduled} tone="blue" />
          <Stat label="Checked in" value={stats.checkedIn} tone="amber" />
          <Stat label="Completed" value={stats.completed} tone="green" />
          <Stat label="Doctors on staff" value={stats.doctors} tone="slate" />
        </section>

        <section className="content-grid">
          <AppointmentsTable
            loading={loading}
            appointments={appointments}
            doctors={doctors}
            filters={filters}
            onFilter={(patch) => setFilters((f) => ({ ...f, ...patch }))}
            onStatus={(a, status) =>
              run(() => api.updateAppointment(a.id, { status }), `${a.patient_name}: ${status.replace('_', ' ').toLowerCase()}`)
            }
            onDelete={(a) => run(() => api.deleteAppointment(a.id), 'Appointment removed')}
          />
          <DoctorsPanel
            doctors={doctors}
            onAdd={(doctor) => run(() => api.createDoctor(doctor), `${doctor.name} added`)}
            onDelete={(d) => run(() => api.deleteDoctor(d.id), `${d.name} removed`)}
          />
        </section>
      </main>

      {showBooking && (
        <BookingModal
          doctors={doctors}
          onClose={() => setShowBooking(false)}
          onBooked={(appt) => {
            setShowBooking(false);
            setToast(`Booked ${appt.patient_name} with ${appt.doctor_name}`);
            load();
          }}
        />
      )}

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}

function Stat({ label, value, tone }) {
  return (
    <div className={`stat ${tone}`}>
      <small>{label}</small>
      <strong>{value}</strong>
    </div>
  );
}
