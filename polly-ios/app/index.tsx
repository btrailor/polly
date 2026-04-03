// Root index — redirect to onboarding or main chat based on gateway config
import { Redirect } from 'expo-router';
import { readOnboardingComplete } from '../src/store/onboardingStore';

export default function Index() {
  const isConfigured = readOnboardingComplete();
  return <Redirect href={isConfigured ? '/(main)/chat' : '/onboarding'} />;
}

