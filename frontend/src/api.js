// Thin wrapper around the ClinicFlow REST API.
// The browser always calls relative /api/* paths; Nginx (Docker Compose) or the
// Kubernetes Ingress routes them to the FastAPI backend.
const API = '/api';

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === 'string') message = body.detail;
      else if (Array.isArray(body.detail)) message = body.detail.map((d) => d.msg).join(', ');
    } catch {
      /* non-JSON error body */
    }
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}

export const api = {
  listDoctors: () => request('/doctors'),
  createDoctor: (doctor) => request('/doctors', { method: 'POST', body: JSON.stringify(doctor) }),
  deleteDoctor: (id) => request(`/doctors/${id}`, { method: 'DELETE' }),

  listAppointments: (filters = {}) => {
    const params = new URLSearchParams(Object.entries(filters).filter(([, v]) => v));
    const query = params.toString();
    return request(`/appointments${query ? `?${query}` : ''}`);
  },
  stats: () => request('/appointments/stats'),
  createAppointment: (appt) => request('/appointments', { method: 'POST', body: JSON.stringify(appt) }),
  updateAppointment: (id, changes) => request(`/appointments/${id}`, { method: 'PUT', body: JSON.stringify(changes) }),
  deleteAppointment: (id) => request(`/appointments/${id}`, { method: 'DELETE' }),
};
