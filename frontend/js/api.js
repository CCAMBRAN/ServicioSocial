/**
 * API.js - Funciones para comunicarse con el backend FastAPI
 */

const API_BASE = "http://127.0.0.1:8000/api/v1";

class API {
    /**
     * Obtener todos los seguros
     */
    static async obtenerSeguros() {
        try {
            const response = await fetch(`${API_BASE}/seguros/`);
            if (!response.ok) throw new Error("Error al obtener seguros");
            return await response.json();
        } catch (error) {
            console.error("Error en obtenerSeguros:", error);
            return [];
        }
    }

    /**
     * Obtener seguros por tipo (basico, estandar, premium)
     */
    static async obtenerSegurosPorTipo(tipo) {
        try {
            const response = await fetch(`${API_BASE}/seguros/economicos/${tipo}`);
            if (!response.ok) throw new Error("Error al obtener seguros por tipo");
            return await response.json();
        } catch (error) {
            console.error(`Error en obtenerSegurosPorTipo(${tipo}):`, error);
            return [];
        }
    }

    /**
     * Crear un nuevo usuario
     */
    static async crearUsuario(datos) {
        try {
            const response = await fetch(`${API_BASE}/usuarios/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    nombre: datos.nombre,
                    email: datos.email,
                    telefono: datos.telefono || null
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || "Error al crear usuario");
            }

            return await response.json();
        } catch (error) {
            console.error("Error en crearUsuario:", error);
            throw error;
        }
    }

    /**
     * Obtener información de un usuario
     */
    static async obtenerUsuario(usuarioId) {
        try {
            // Nota: Este endpoint no existe aún. Usar datos locales por ahora.
            return JSON.parse(localStorage.getItem("usuario"));
        } catch (error) {
            console.error("Error en obtenerUsuario:", error);
            return null;
        }
    }

    /**
     * Comprar un seguro
     */
    static async comprarSeguro(usuarioId, seguroId) {
        try {
            const response = await fetch(`${API_BASE}/usuarios/${usuarioId}/comprar-seguro`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    seguro_id: seguroId
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || "Error al comprar seguro");
            }

            return await response.json();
        } catch (error) {
            console.error("Error en comprarSeguro:", error);
            throw error;
        }
    }

    /**
     * Pagar cuota mensual
     */
    static async pagarCuota(polizaId, metodoPago = "saldo") {
        try {
            const response = await fetch(`${API_BASE}/polizas/${polizaId}/pagar-cuota`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    poliza_id: polizaId,
                    metodo_pago: metodoPago
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || "Error al pagar cuota");
            }

            return await response.json();
        } catch (error) {
            console.error("Error en pagarCuota:", error);
            throw error;
        }
    }

    /**
     * Obtener próximos pagos del usuario
     */
    static async obtenerProximosPagos(usuarioId) {
        try {
            const response = await fetch(`${API_BASE}/usuarios/${usuarioId}/proximos-pagos`);
            if (!response.ok) throw new Error("Error al obtener próximos pagos");
            return await response.json();
        } catch (error) {
            console.error("Error en obtenerProximosPagos:", error);
            return { proximos_pagos: [] };
        }
    }
}

/**
 * Funciones de almacenamiento local
 */
const Storage = {
    guardarUsuario(usuario) {
        localStorage.setItem("usuario", JSON.stringify(usuario));
    },

    obtenerUsuario() {
        const usuario = localStorage.getItem("usuario");
        return usuario ? JSON.parse(usuario) : null;
    },

    eliminarUsuario() {
        localStorage.removeItem("usuario");
    },

    existeUsuario() {
        return !!localStorage.getItem("usuario");
    }
};
