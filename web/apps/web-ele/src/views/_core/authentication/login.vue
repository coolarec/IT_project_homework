<script lang="ts" setup>
import type { VbenFormSchema } from '@vben/common-ui';

import { computed, markRaw } from 'vue';

import { AuthenticationLogin, SliderCaptcha, z } from '@vben/common-ui';
import { $t } from '@vben/locales';

import { ElMessage } from 'element-plus';

import {
  getGiteeAuthorizeUrlApi,
  getGitHubAuthorizeUrlApi,
  getGoogleAuthorizeUrlApi,
  getMicrosoftAuthorizeUrlApi,
} from '#/api/core';
import { useAuthStore } from '#/store';

defineOptions({ name: 'Login' });

type OAuthProvider = {
  iconFill?: string;
  iconPath: string;
  iconViewBox: string;
  label: string;
  loginErrorKey: string;
  requestAuthorizeUrl: () => Promise<{ authorize_url?: string } | null | undefined>;
};

const authStore = useAuthStore();

const formSchema = computed((): VbenFormSchema[] => {
  return [
    {
      component: 'VbenInput',
      componentProps: {
        autocomplete: 'username',
        clearable: true,
        maxlength: 64,
        placeholder: $t('authentication.usernameTip'),
        trim: true,
      },
      defaultValue: '',
      fieldName: 'username',
      label: $t('authentication.username'),
      rules: z
        .string()
        .trim()
        .min(1, { message: $t('authentication.usernameTip') })
        .max(64, { message: $t('authentication.usernameTip') }),
    },
    {
      component: 'VbenInputPassword',
      componentProps: {
        autocomplete: 'current-password',
        maxlength: 64,
        showPassword: true,
        placeholder: $t('authentication.password'),
      },
      defaultValue: '',
      fieldName: 'password',
      label: $t('authentication.password'),
      rules: z
        .string()
        .min(6, { message: $t('authentication.passwordTip') })
        .max(64, { message: $t('authentication.passwordTip') }),
    },
    {
      component: markRaw(SliderCaptcha),
      fieldName: 'captcha',
      rules: z.boolean().refine((value) => value, {
        message: $t('authentication.verifyRequiredTip'),
      }),
    },
  ];
});

const oauthProviderRows = computed<OAuthProvider[][]>(() => [
  [
    {
      iconFill: '#C71D23',
      iconPath:
        'M512 1024C229.222 1024 0 794.778 0 512S229.222 0 512 0s512 229.222 512 512-229.222 512-512 512z m259.149-568.883h-290.74a25.293 25.293 0 0 0-25.292 25.293l-0.026 63.206c0 13.952 11.315 25.293 25.267 25.293h177.024c13.978 0 25.293 11.315 25.293 25.267v12.646a75.853 75.853 0 0 1-75.853 75.853h-240.23a25.293 25.293 0 0 1-25.267-25.293V417.203a75.853 75.853 0 0 1 75.827-75.853h353.946a25.293 25.293 0 0 0 25.267-25.292l0.077-63.207a25.293 25.293 0 0 0-25.268-25.293H417.152a189.62 189.62 0 0 0-189.62 189.645V771.15c0 13.977 11.316 25.293 25.294 25.293h372.94a170.65 170.65 0 0 0 170.65-170.65V480.384a25.293 25.293 0 0 0-25.293-25.267z',
      iconViewBox: '0 0 1024 1024',
      label: 'Gitee',
      loginErrorKey: 'authentication.giteeLoginFailed',
      requestAuthorizeUrl: getGiteeAuthorizeUrlApi,
    },
    {
      iconPath:
        'M512 42.666667A464.64 464.64 0 0 0 42.666667 502.186667 460.373333 460.373333 0 0 0 363.52 938.666667c23.466667 4.266667 32-9.813333 32-22.186667v-78.08c-130.56 27.733333-158.293333-61.44-158.293333-61.44a122.026667 122.026667 0 0 0-52.053334-67.413333c-42.666667-28.16 3.413333-27.733333 3.413334-27.733334a98.56 98.56 0 0 1 71.68 47.36 101.12 101.12 0 0 0 136.533333 37.973334 99.413333 99.413333 0 0 1 29.866667-61.44c-104.106667-11.52-213.333333-50.773333-213.333334-226.986667a177.066667 177.066667 0 0 1 47.36-124.16 161.28 161.28 0 0 1 4.693334-121.173333s39.68-12.373333 128 46.933333a455.68 455.68 0 0 1 234.666666 0c89.6-59.306667 128-46.933333 128-46.933333a161.28 161.28 0 0 1 4.693334 121.173333A177.066667 177.066667 0 0 1 810.666667 477.866667c0 176.64-110.08 215.466667-213.333334 226.986666a106.666667 106.666667 0 0 1 32 85.333334v125.866666c0 14.933333 8.533333 26.88 32 22.186667A460.8 460.8 0 0 0 981.333333 502.186667 464.64 464.64 0 0 0 512 42.666667',
      iconViewBox: '0 0 1024 1024',
      label: 'GitHub',
      loginErrorKey: 'authentication.githubLoginFailed',
      requestAuthorizeUrl: getGitHubAuthorizeUrlApi,
    },
  ],
  [
    {
      iconPath:
        'M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z',
      iconViewBox: '0 0 24 24',
      label: 'Google',
      loginErrorKey: 'authentication.googleLoginFailed',
      requestAuthorizeUrl: getGoogleAuthorizeUrlApi,
    },
    {
      iconPath:
        'M0 0h10.66v10.66H0z M12.34 0h10.66v10.66H12.34z M0 12.34h10.66V23H0z M12.34 12.34h10.66V23H12.34z',
      iconViewBox: '0 0 23 23',
      label: 'Microsoft',
      loginErrorKey: 'authentication.microsoftLoginFailed',
      requestAuthorizeUrl: getMicrosoftAuthorizeUrlApi,
    },
  ],
]);

const redirectToOAuth = (url?: string) => {
  if (url) {
    window.location.href = url;
    return;
  }
  ElMessage.error($t('authentication.getAuthUrlFailed'));
};

async function handleOAuthLogin(provider: OAuthProvider) {
  try {
    const data = await provider.requestAuthorizeUrl();
    redirectToOAuth(data?.authorize_url);
  } catch (error) {
    console.error(`${provider.label} 登录失败:`, error);
    ElMessage.error($t(provider.loginErrorKey));
  }
}
</script>

<template>
  <AuthenticationLogin
    :form-schema="formSchema"
    :loading="authStore.loginLoading"
    :show-third-party-login="false"
    @submit="authStore.authLogin"
  >
    <template #third-party-login>
      <div class="mt-4 w-full sm:mx-auto md:max-w-md">
        <div class="flex items-center justify-between">
          <span class="border-input w-[35%] border-b dark:border-gray-600"></span>
          <span class="text-muted-foreground text-center text-xs uppercase">
            {{ $t('authentication.thirdPartyLogin') }}
          </span>
          <span class="border-input w-[35%] border-b dark:border-gray-600"></span>
        </div>

        <div
          v-for="(providerRow, rowIndex) in oauthProviderRows"
          :key="rowIndex"
          class="mt-4 flex justify-center gap-2"
        >
          <button
            v-for="provider in providerRow"
            :key="provider.label"
            type="button"
            class="hover:bg-accent hover:text-accent-foreground border-input bg-background text-muted-foreground flex min-w-[120px] cursor-pointer items-center justify-center gap-2 rounded-lg border px-5 py-2 text-sm shadow-sm transition-all duration-300 hover:shadow-md"
            @click="handleOAuthLogin(provider)"
          >
            <svg
              class="size-4 shrink-0"
              :viewBox="provider.iconViewBox"
              xmlns="http://www.w3.org/2000/svg"
              :fill="provider.iconFill || 'currentColor'"
            >
              <path :d="provider.iconPath" />
            </svg>
            <span>{{ provider.label }}</span>
          </button>
        </div>
      </div>
    </template>
  </AuthenticationLogin>
</template>
