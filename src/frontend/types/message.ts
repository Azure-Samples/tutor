export interface Message {
  id: number;
  sender: 'user' | 'bot';
  content: string;
}