import pool from '../../lib/db.js';

export async function post({ request }) {
  try {
    const { name, last_name, email, userName, password } = await request.json();

    // Insertar el usuario en la base de datos con tipo predeterminado 1
    const query = `INSERT INTO users (name, last_name, email, userName, password, type) VALUES (?, ?, ?, ?, ?, 1)`;
    const [result] = await pool.execute(query, [name, last_name, email, userName, password]);

    return {
      status: 201,
      body: JSON.stringify({ message: 'Usuario registrado exitosamente' }),
    };
  } catch (error) {
    console.error('Error al registrar el usuario:', error);
    return {
      status: 500,
      body: JSON.stringify({ error: 'Error al registrar el usuario' }),
    };
  }
}
