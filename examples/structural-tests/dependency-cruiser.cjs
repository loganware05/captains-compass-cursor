/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: "no-circular",
      severity: "error",
      from: {},
      to: { circular: true },
    },
    {
      name: "ui-not-to-db",
      comment: "UI must not import database modules directly",
      severity: "error",
      from: { path: "^src/ui" },
      to: { path: "^src/db" },
    },
  ],
  options: {
    doNotFollow: { path: "node_modules" },
  },
};
