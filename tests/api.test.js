import request from "supertest";
import app from "../src/app.js";

describe("API Integration Tests", () => {

  test("GET /events retourne une liste paginée", async () => {
    const res = await request(app).get("/events?page=1&limit=5");

    expect(res.statusCode).toBe(200);
    expect(res.body.events).toBeDefined();
    expect(res.body.events.length).toBeLessThanOrEqual(5);
  });

  test("GET /stats retourne les statistiques", async () => {
    const res = await request(app).get("/stats");

    expect(res.statusCode).toBe(200);
    expect(res.body.total_events).toBeDefined();
    expect(Array.isArray(res.body.by_category)).toBe(true);
  });

});