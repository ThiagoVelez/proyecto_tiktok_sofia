/**
 * Tipos de datos estrictos para el Frontend de Follow.
 * Basados en los esquemas de MySQL y contratos de la API FastAPI.
 */

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  bio?: string;
  avatar_url?: string;
  role: 'user' | 'creator' | 'moderator' | 'admin';
  is_verified: boolean;
  following_count?: number;
  followers_count?: number;
  likes_count?: number;
}

export interface Sound {
  id: number;
  title: string;
  artist_name: string;
  audio_url: string;
  cover_url: string;
  duration_seconds: number;
  usage_count: number;
}

export interface Hashtag {
  id: number;
  tag: string;
  videos_count: number;
  views_count: number;
}

export interface Video {
  id: number;
  user_id: number;
  sound_id?: number;
  title: string;
  description: string;
  video_url: string;
  thumbnail_url: string;
  duration_seconds: number;
  views_count: number;
  likes_count: number;
  comments_count: number;
  shares_count: number;
  visibility: 'public' | 'friends' | 'private';
  allow_comments: boolean;
  allow_duet: boolean;
  audience_rating: string;
  author?: User;
  sound?: Sound;
  tags?: string[];
  is_liked?: boolean;
  is_bookmarked?: boolean;
  is_following?: boolean;
}

export interface Comment {
  id: number;
  video_id: number;
  user_id?: number;
  content: string;
  likes_count: number;
  created_at: string;
  user?: {
    id: number;
    username: string;
    avatar_url: string;
    is_verified?: boolean;
    is_creator?: boolean;
  };
  author?: {
    id: number;
    username: string;
    avatar_url: string;
    is_verified?: boolean;
  };
  is_pinned?: boolean;
  is_liked?: boolean;
}

export interface Story {
  id: number;
  user_id: number;
  media_url: string;
  media_type: 'image' | 'video';
  caption?: string;
  views_count: number;
  expires_at: string;
  user?: User;
  has_unseen?: boolean;
}
