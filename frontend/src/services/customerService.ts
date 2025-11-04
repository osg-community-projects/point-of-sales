import api from '@/lib/api';

export interface Customer {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  created_at: string;
}

export interface CreateCustomerData {
  name: string;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
}

export interface UpdateCustomerData extends Partial<CreateCustomerData> {
  id: number;
}

class CustomerService {
  async getCustomers(): Promise<Customer[]> {
    const response = await api.get('/customers/');
    return response.data;
  }

  async getCustomer(id: number): Promise<Customer> {
    const response = await api.get(`/customers/${id}`);
    return response.data;
  }

  async createCustomer(customerData: CreateCustomerData): Promise<Customer> {
    const response = await api.post('/customers/', customerData);
    return response.data;
  }

  async updateCustomer(id: number, customerData: Partial<CreateCustomerData>): Promise<Customer> {
    const response = await api.put(`/customers/${id}`, customerData);
    return response.data;
  }

  async deleteCustomer(id: number): Promise<void> {
    await api.delete(`/customers/${id}`);
  }

  async searchCustomers(query: string): Promise<Customer[]> {
    const response = await api.get('/customers/search', {
      params: { q: query }
    });
    return response.data;
  }
}

export const customerService = new CustomerService();
