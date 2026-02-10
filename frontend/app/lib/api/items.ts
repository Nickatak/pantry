/**
 * Items API endpoints
 * Handles CRUD operations for pantry items
 */

import { apiCall } from './core';

export interface Item {
  id: number;
  barcode: string;
  title: string;
  description: string;
  alias: string;
  category: string;
  quantity?: number;
}

export interface ItemsListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Item[];
}

/**
 * Get paginated list of items with optional search
 *
 * @param page - Page number (1-based)
 * @param pageSize - Items per page (default 20, max 100)
 * @param search - Optional search query (searches title, description, alias, barcode)
 * @returns Paginated items list
 */
export async function getItems(
  page: number = 1,
  pageSize: number = 20,
  search: string = ''
): Promise<ItemsListResponse> {
  const params = new URLSearchParams();
  params.append('page', String(page));
  params.append('page_size', String(pageSize));
  if (search) {
    params.append('search', search);
  }

  return apiCall(`/items/?${params.toString()}`, {
    method: 'GET',
  });
}

/**
 * Get a single item by ID
 *
 * @param id - Item ID
 * @returns Item data
 */
export async function getItem(id: number): Promise<Item> {
  return apiCall(`/items/${id}/`, {
    method: 'GET',
  });
}

/**
 * Update an item
 *
 * @param id - Item ID
 * @param data - Fields to update
 * @returns Updated item data
 */
export async function updateItem(
  id: number,
  data: Partial<Omit<Item, 'id' | 'barcode'>>
): Promise<Item> {
  return apiCall(`/items/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * Update quantity for a user-owned item
 *
 * @param id - Item ID
 * @param quantity - New quantity (must be >= 1)
 * @returns Updated item data
 */
export async function updateItemQuantity(
  id: number,
  quantity: number
): Promise<Item> {
  return updateItem(id, { quantity });
}

/**
 * Delete an item
 *
 * @param id - Item ID
 */
export async function deleteItem(id: number): Promise<void> {
  await apiCall(`/items/${id}/`, {
    method: 'DELETE',
  });
}
