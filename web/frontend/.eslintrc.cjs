module.exports = {
	extends: [
		"eslint:recommended",
		"plugin:@typescript-eslint/recommended",
		"plugin:react/recommended",
		"plugin:react-hooks/recommended",
		"plugin:prettier/recommended",
	],
	parser: "@typescript-eslint/parser",
	plugins: ["@typescript-eslint", "react", "react-hooks"],
	env: { browser: true, es2021: true, node: true, jest: true },
	settings: { react: { version: "detect" } },
	rules: {
		"react/prop-types": "off",
		"@typescript-eslint/no-explicit-any": "warn",
		"@typescript-eslint/consistent-type-imports": "error",
	},
};
