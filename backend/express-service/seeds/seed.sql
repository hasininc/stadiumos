INSERT INTO users (id, email, password_hash, role) VALUES
('usr-001', 'director@stadiumos.fifa.org', '$2b$10$3e4r5t6y7u8i9o0pQWERTYuiopasdghjklzxcvbnm1234567890', 'ops_manager'),
('usr-002', 'volunteer.mateo@stadiumos.fifa.org', '$2b$10$3e4r5t6y7u8i9o0pQWERTYuiopasdghjklzxcvbnm1234567890', 'volunteer')
ON CONFLICT DO NOTHING;

INSERT INTO user_preferences (user_id, theme, language, notifications_enabled) VALUES
('usr-001', 'dark', 'en', TRUE),
('usr-002', 'dark', 'es', TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO tickets (id, holder_name, seat_number, stadium_id, validated) VALUES
('tkt-001', 'John Doe', 'Sec 102, Row 12, Seat 4', 'STAD_01_USA', FALSE),
('tkt-002', 'Jane Smith', 'Sec 104, Row 5, Seat 18', 'STAD_01_USA', FALSE)
ON CONFLICT DO NOTHING;
