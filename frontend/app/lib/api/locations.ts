/**
 * Locations API endpoints
 */

import { apiCall } from './core';

export interface Location {
  id: number;
  name: string;
}

export async function getLocations(): Promise<Location[]> {
  return apiCall('/locations/', {
    method: 'GET',
  });
}

export async function createLocation(name: string): Promise<Location> {
  return apiCall('/locations/', {
    method: 'POST',
    body: JSON.stringify({ name }),
  });
}
