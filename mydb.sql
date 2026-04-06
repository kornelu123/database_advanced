CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(60) NOT NULL UNIQUE,
    display_name VARCHAR(100),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    phone VARCHAR(20),
    city VARCHAR(100),
    avatar_url VARCHAR(500),
    bio TEXT,
    rating DECIMAL(3,2) DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id SMALLSERIAL PRIMARY KEY,
    name VARCHAR(60) NOT NULL UNIQUE,
    icon_name VARCHAR(100),
    description TEXT
);

CREATE TABLE voivodeships (
    id SMALLSERIAL PRIMARY KEY,
    name VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    voivodeship_id SMALLINT NOT NULL REFERENCES voivodeships(id) ON DELETE RESTRICT,
    name VARCHAR(100) NOT NULL,
    postal_code_prefix VARCHAR(2),
    UNIQUE (voivodeship_id, name)
);

CREATE TABLE items (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(120) NOT NULL,
    description TEXT,
    condition VARCHAR(30),
    quantity SMALLINT DEFAULT 1,
    city_id INT REFERENCES cities(id) ON DELETE SET NULL,
    street_hint VARCHAR(120),
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    taken_at TIMESTAMP,
    taken_by_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    views_count INT DEFAULT 0,
    favorites_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '30 days'
);

CREATE TABLE item_photos (
    id BIGSERIAL PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    storage_key VARCHAR(200),
    is_main BOOLEAN,
    position SMALLINT,
    width INT,
    height INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reservations (
    id BIGSERIAL PRIMARY KEY,
    item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reserved_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE item_categories (
    item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    category_id SMALLINT NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, category_id)
);

CREATE INDEX idx_items_user_id ON items(user_id);
CREATE INDEX idx_items_city_id ON items(city_id);
CREATE INDEX idx_items_status ON items(status);
CREATE INDEX idx_items_created_at ON items(created_at);
CREATE INDEX idx_items_expires_at ON items(expires_at);

CREATE INDEX idx_reservations_item_id ON reservations(item_id);
CREATE INDEX idx_reservations_user_id ON reservations(user_id);
CREATE INDEX idx_reservations_status ON reservations(status);
CREATE INDEX idx_reservations_expires_at ON reservations(expires_at) WHERE status = 'active';

CREATE INDEX idx_item_photos_item_id ON item_photos(item_id);

CREATE INDEX idx_cities_voivodeship_id ON cities(voivodeship_id);
CREATE INDEX idx_cities_name ON cities(name);
