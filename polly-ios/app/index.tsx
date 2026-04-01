// Root index — redirect to onboarding or main chat based on gateway config
import { Redirect } from 'expo-router';
import { readOnboardingComplete } from '../src/store/onboardingStore';

const isConfigured = readOnboardingComplete();

export default function Index() {
  return <Redirect href={isConfigured ? '/(main)/chat' : '/onboarding'} />;
}
