import api from '@/lib/api';

export interface OrderItem {
  id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
  total_price: number;
  product: {
    id: number;
    name: string;
  };
}

export interface Order {
  id: number;
  order_number: string;
  customer_id: number | null;
  customer: {
    id: number;
    name: string;
    email: string;
  } | null;
  user_id: number;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  payment_method: string | null;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string | null;
  order_items: OrderItem[];
}

export interface CreateOrderData {
  customer_id?: number | null;
  payment_method: string;
  discount_amount?: number;
  notes?: string | null;
  items: {
    product_id: number;
    quantity: number;
    unit_price: number;
  }[];
}

export interface UpdateOrderData {
  customer_id?: number | null;
  payment_method?: string;
  discount_amount?: number;
  notes?: string | null;
  status?: string;
}

class OrderService {
  async getOrders(): Promise<Order[]> {
    const response = await api.get('/orders/');
    return response.data;
  }

  async getOrder(id: number): Promise<Order> {
    const response = await api.get(`/orders/${id}`);
    return response.data;
  }

  async getOrderByNumber(orderNumber: string): Promise<Order> {
    const response = await api.get(`/orders/number/${orderNumber}`);
    return response.data;
  }

  async createOrder(orderData: CreateOrderData): Promise<Order> {
    const response = await api.post('/orders/', orderData);
    return response.data;
  }

  async updateOrder(id: number, orderData: UpdateOrderData): Promise<Order> {
    const response = await api.put(`/orders/${id}`, orderData);
    return response.data;
  }

  async deleteOrder(id: number): Promise<void> {
    await api.delete(`/orders/${id}`);
  }

  async completeOrder(id: number): Promise<Order> {
    const response = await api.post(`/orders/${id}/complete`);
    return response.data;
  }

  async cancelOrder(id: number): Promise<Order> {
    const response = await api.post(`/orders/${id}/cancel`);
    return response.data;
  }

  async refundOrder(id: number): Promise<Order> {
    const response = await api.post(`/orders/${id}/refund`);
    return response.data;
  }
}

export const orderService = new OrderService();
