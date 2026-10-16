const STATUSES = ['SCHEDULED', 'CHECKED_IN', 'COMPLETED', 'CANCELLED'];

const label = (status) => status.replace('_', ' ').toLowerCase();

function formatWhen(iso) {
  const d = new Date(iso);
  return {
    date: d.toLocaleDateString(undefined, { day: 'numeric', month: 'short' }),
    time: d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }),
  };
}

export default function AppointmentsTable({ loading, appointments, doctors, filters, onFilter, onStatus, onDelete }) {
  return (
    <div className="panel" id="appointments">
      <div className="panel-head">
        <div>
          <h2>Appointments</h2>
          <p className="muted">{appointments.length} shown</p>
        </div>
        <div className="filter-bar">
          <select aria-label="Filter by status" value={filters.status} onChange={(e) => onFilter({ status: e.target.value })}>
            <option value="">All statuses</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>{label(s)}</option>
            ))}
          </select>
          <select aria-label="Filter by doctor" value={filters.doctor_id} onChange={(e) => onFilter({ doctor_id: e.target.value })}>
            <option value="">All doctors</option>
            {doctors.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
          <input aria-label="Filter by date" type="date" value={filters.on} onChange={(e) => onFilter({ on: e.target.value })} />
        </div>
      </div>

      {loading ? (
        <div className="empty">Loading appointments…</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>When</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Status</th>
                <th className="right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {appointments.map((a) => {
                const when = formatWhen(a.scheduled_at);
                return (
                  <tr key={a.id}>
                    <td data-label="When">
                      <b>{when.time}</b>
                      <small>{when.date} · {a.duration_minutes} min</small>
                    </td>
                    <td data-label="Patient">
                      <b>{a.patient_name}</b>
                      <small>{a.reason || a.patient_phone || '—'}</small>
                    </td>
                    <td data-label="Doctor">
                      <b>{a.doctor_name}</b>
                      <small>{a.specialty}</small>
                    </td>
                    <td data-label="Status">
                      <span className={`badge ${a.status.toLowerCase()}`}>{label(a.status)}</span>
                    </td>
                    <td className="right actions">
                      {a.status === 'SCHEDULED' && <button onClick={() => onStatus(a, 'CHECKED_IN')}>Check in</button>}
                      {a.status === 'CHECKED_IN' && <button onClick={() => onStatus(a, 'COMPLETED')}>Complete</button>}
                      {(a.status === 'SCHEDULED' || a.status === 'CHECKED_IN') && (
                        <button className="ghost" onClick={() => onStatus(a, 'CANCELLED')}>Cancel</button>
                      )}
                      <button className="ghost danger" title="Delete" aria-label="Delete appointment" onClick={() => onDelete(a)}>
                        ✕
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {!appointments.length && <div className="empty">No appointments match these filters.</div>}
        </div>
      )}
    </div>
  );
}
