import express from "express";
import { Issuer, generators } from "openid-client";
import open from "open";
import { readFileSync, writeFileSync } from "fs";
import { stringify } from "querystring";

// Configuration for Azure AD B2C
// Read the config.json file
const configData = readFileSync("config.json");
const config = JSON.parse(configData);

// Extract the variables from the config object
const { tenantName, clientId, policyName, redirectPort, scope } = config;
const redirectUri = `http://localhost:${redirectPort}/callback`;

// Generate the code verifier and challenge
const codeVerifier = generators.codeVerifier();
const codeChallenge = generators.codeChallenge(codeVerifier);

// Create the Express app
const app = express();

// Create the Azure AD B2C issuer
const issuer = await Issuer.discover(
  `https://${tenantName}.b2clogin.com/${tenantName}.onmicrosoft.com/${policyName}/v2.0/.well-known/openid-configuration`
);

// Create the client
const client = new issuer.Client({
  client_id: clientId,
  redirect_uris: [redirectUri],
  response_types: ["code"],
  token_endpoint_auth_method: "none",
});

app.get("/callback", async (req, res) => {
  const params = req.query;

  try {
    const tokenSet = await client.callback(redirectUri, params, {
      code_verifier: codeVerifier,
    });
    const viewerParams = {
      endpoint: "https://devtest.newpage.app/graphql/v1/graphql",
      header: `Authorization: Bearer ${tokenSet.id_token}`,
    };
    const queryString = stringify(viewerParams);

    res.redirect(`https://cloud.hasura.io/public/graphiql?${queryString}`);
    // res.send("Login successful! Redirecting to API.");
    console.log("Token Set:", tokenSet);
    writeFileSync("token.json", JSON.stringify(tokenSet));
  } catch (error) {
    res.send("Error during login process. Please try again.");
    console.error("Callback Error:", error);
  }

  process.exit();
});

app.listen(redirectPort, async () => {
  console.log(`Server is listening on http://localhost:${redirectPort}`);

  const authUrl = client.authorizationUrl({
    scope,
    code_challenge: codeChallenge,
    code_challenge_method: "S256",
  });

  console.log("Login URL:", authUrl);
  await open(authUrl);
});
