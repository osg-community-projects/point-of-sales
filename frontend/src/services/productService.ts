import api from '@/lib/api';

export interface Product {
  id: number;
  name: string;
  description: string | null;
  price: number;
  cost: number;
  sku: string | null;
  barcode: string | null;
  stock_quantity: number;
  min_stock_level: number;
  is_active: boolean;
  category: {
    id: number;
    name: string;
  } | null;
  created_at: string;
}

export interface CreateProductData {
  name: string;
  description?: string | null;
  price: number;
  cost?: number;
  sku?: string | null;
  barcode?: string | null;
  stock_quantity?: number;
  min_stock_level?: number;
  category_id?: number | null;
}

export interface UpdateProductData extends Partial<CreateProductData> {
  id: number;
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
}

class ProductService {
  async getProducts(activeOnly: boolean = false): Promise<Product[]> {
    const params = activeOnly ? { active_only: 'true' } : {};
    const response = await api.get('/products/', { params });
    return response.data;
  }

  async getProduct(id: number): Promise<Product> {
    const response = await api.get(`/products/${id}`);
    return response.data;
  }

  async createProduct(productData: CreateProductData): Promise<Product> {
    const response = await api.post('/products/', productData);
    return response.data;
  }

  async updateProduct(id: number, productData: Partial<CreateProductData>): Promise<Product> {
    const response = await api.put(`/products/${id}`, productData);
    return response.data;
  }

  async deleteProduct(id: number): Promise<void> {
    await api.delete(`/products/${id}`);
  }

  async getCategories(): Promise<Category[]> {
    const response = await api.get('/products/categories');
    return response.data;
  }

  async createCategory(name: string, description?: string): Promise<Category> {
    const response = await api.post('/products/categories', { name, description });
    return response.data;
  }

  async updateCategory(id: number, name: string, description?: string): Promise<Category> {
    const response = await api.put(`/products/categories/${id}`, { name, description });
    return response.data;
  }

  async deleteCategory(id: number): Promise<void> {
    await api.delete(`/products/categories/${id}`);
  }
}

export const productService = new ProductService();
