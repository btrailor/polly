// Root index — redirect to onboarding or main chat based on gateway config
import { Redirect } from 'expo-router';

// TODO: check expo-secure-store for stored gateway token
// If configured → redirect to /(main)/chat
// If not → redirect to /onboarding
const isConfigured = false; // placeholder — wire to store in next commit

export default function Index() {
  return <Redirect href={isConfigured ? '/(main)/chat' : '/onboarding'} />;
}
