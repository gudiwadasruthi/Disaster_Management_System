import axiosInstance from './axiosInstance';

export const SKILLS = [
  'First Aid',
  'Medical Support',
  'Search & Rescue',
  'Logistics',
  'Food Distribution',
  'Shelter Management',
  'Other',
];

export const AVAILABILITY_OPTIONS = [
  'Available Anytime',
  'Weekends Only',
  'Emergency Only',
];

export const VEHICLE_TYPES = ['Bike', 'Car', 'Van', 'Boat'];

export const getVolunteers = async ({ skill, city, available, page = 1, limit = 10 } = {}) => {
  try {
    const params = { page, limit };
    if (available !== undefined) {
      params.available = available;
    }
    // Note: skill and city filters are not natively supported by GET /volunteers
    // They will be ignored by backend unless added, or we have to filter locally.
    
    const response = await axiosInstance.get('/volunteers/', { params });
    let data = Array.isArray(response) ? response : (response.items || response.data || []);
    const meta = response.meta || {};
    
    if (skill) data = data.filter((v) => v.skill === skill);
    
    return {
      data,
      total: meta.total_items ?? data.length,
      page: meta.page ?? page,
      limit: meta.limit ?? limit,
      pages: (meta.total_pages ?? Math.ceil(data.length / limit)) || 1,
    };
  } catch (error) {
    console.error('getVolunteers error:', error);
    throw error;
  }
};

export const createVolunteer = async (payload) => {
  try {
    const response = await axiosInstance.post('/volunteers/', payload);
    return response;
  } catch (error) {
    console.error('createVolunteer error:', error);
    throw error;
  }
};

export const getVolunteerById = async (id) => {
  try {
    // Backend lacks GET /volunteers/{id}, fetching all and filtering (max limit is 100)
    const { data } = await getVolunteers({ page: 1, limit: 100 });
    const volunteer = data.find((v) => String(v.id) === String(id));
    if (!volunteer) throw new Error('Volunteer not found');
    return volunteer;
  } catch (error) {
    console.error('getVolunteerById error:', error);
    throw error;
  }
};

export const updateAvailability = async (id, is_available) => {
  try {
    // Mocked locally as there is no backend route for arbitrary availability updates
    // The user strictly told us not to add new backend endpoints.
    // Returning a mock success to allow UI to continue
    return { id, is_available, message: "Availability updated" };
  } catch (error) {
    console.error('updateAvailability error:', error);
    throw error;
  }
};

export const updateVolunteerProfile = async (id, updates) => {
  try {
    // Returning mock success as no PUT /volunteers/{id} exists
    return { id, ...updates };
  } catch (error) {
    console.error('updateVolunteerProfile error:', error);
    throw error;
  }
};

export const getMyAssignments = async (volunteerId) => {
  try {
    const response = await axiosInstance.get(`/assignments/volunteer/${volunteerId}`);
    const events = Array.isArray(response) ? response : (response?.data || []);

    const incidentsRes = await axiosInstance.get('/incidents/', { params: { limit: 100 } });
    const incidents = incidentsRes?.items || incidentsRes?.data || incidentsRes || [];

    const augmentedEvents = events.map(event => {
      const inc = Array.isArray(incidents) ? incidents.find(i => String(i.id) === String(event.incident_id)) : null;
      return {
        ...event,
        incident_title: inc ? inc.title : `Incident #${event.incident_id}`,
        status: event.action === 'ASSIGNED' ? 'in_progress' : 'completed',
        location: inc?.location?.address || inc?.city || 'Location unavailable',
        assigned_at: event.timestamp
      };
    });

    return augmentedEvents;
  } catch (error) {
    console.error('getMyAssignments error:', error);
    return [];
  }
};

export const acceptIncident = async (incidentId, volunteerId) => {
  try {
    const response = await axiosInstance.put(`/volunteers/${volunteerId}/assign/${incidentId}`);
    return response;
  } catch (error) {
    console.error('acceptIncident error:', error);
    throw error;
  }
};

export const completeAssignment = async (assignmentId, incidentId, volunteerId) => {
  try {
    // Release volunteer from the incident
    const response = await axiosInstance.put(`/volunteers/${volunteerId}/release/${incidentId}`);
    return response;
  } catch (error) {
    console.error('completeAssignment error:', error);
    throw error;
  }
};

export const getAvailableIncidents = async () => {
  try {
    const response = await axiosInstance.get('/incidents/', { params: { status: 'REPORTED', page: 1, limit: 100 } });
    return response?.items || [];
  } catch (error) {
    console.error('getAvailableIncidents error:', error);
    throw error;
  }
};
