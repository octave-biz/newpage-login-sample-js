import { readFileSync } from "fs";

const url = "https://devtest.newpage.app/graphql/v1/graphql";
const tokenFilePath = "../../token.json";
let token;
try {
  const tokenFileContent = readFileSync(tokenFilePath, "utf8");
  const tokenJson = JSON.parse(tokenFileContent);
  token = tokenJson.id_token;
  if (!token) {
    throw new Error("Token not found in token file");
  }
} catch (error) {
  console.error("Error parsing token file:", error.message);
  console.log(
    "Run npm start at the root of the project in order to generate the token file"
  );
  process.exit(1);
}

const headers = {
  Authorization: `Bearer ${token}`,
  "Content-Type": "application/json",
};

const query = `
query MyQuery {
    carrier {
      id
      label
      createdAt
      updatedAt
    }
  }
`;

fetch(url, {
  method: "POST",
  headers: headers,
  body: JSON.stringify({ query }),
})
  .then((response) => response.json())
  .then((data) => console.log(JSON.stringify(data, null, "  ")))
  .catch((error) => console.error("Error:", error));
