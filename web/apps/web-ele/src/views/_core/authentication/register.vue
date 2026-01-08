<script lang="ts" setup>
import type { VbenFormSchema } from '@vben/common-ui';
import type { Recordable } from '@vben/types';
import { ElMessage } from 'element-plus';
import { computed, h, ref } from 'vue';
import { useRouter } from 'vue-router'; // 导入路由用于跳转

import { AuthenticationRegister, z } from '@vben/common-ui';
import { $t } from '@vben/locales';
import { registerApi } from "#/api/core/user"
defineOptions({ name: 'Register' });

const loading = ref(false);
const router = useRouter();

const formSchema = computed((): VbenFormSchema[] => {
  return [
    {
      component: 'VbenInput',
      componentProps: {
        placeholder: $t('authentication.usernameTip'),
      },
      fieldName: 'username',
      label: $t('authentication.username'),
      rules: z.string().min(1, { message: $t('authentication.usernameTip') }),
    },
    {
      component: 'VbenInputPassword',
      componentProps: {
        passwordStrength: true,
        placeholder: $t('authentication.password'),
      },
      fieldName: 'password',
      label: $t('authentication.password'),
      renderComponentContent() {
        return {
          strengthText: () => $t('authentication.passwordStrength'),
        };
      },
      rules: z.string().min(1, { message: $t('authentication.passwordTip') }),
    },
    {
      component: 'VbenInputPassword',
      componentProps: {
        placeholder: $t('authentication.confirmPassword'),
      },
      dependencies: {
        rules(values) {
          const { password } = values;
          return z
            .string({ required_error: $t('authentication.passwordTip') })
            .min(1, { message: $t('authentication.passwordTip') })
            .refine((value) => value === password, {
              message: $t('authentication.confirmPasswordTip'),
            });
        },
        triggerFields: ['password'],
      },
      fieldName: 'confirmPassword',
      label: $t('authentication.confirmPassword'),
    },
    {
      component: 'VbenCheckbox',
      fieldName: 'agreePolicy',
      renderComponentContent: () => ({
        default: () =>
          h('span', [
            $t('authentication.agree'),
            h(
              'a',
              {
                class: 'vben-link ml-1 ',
                href: '',
              },
              `${$t('authentication.privacyPolicy')} & ${$t('authentication.terms')}`,
            ),
          ]),
      }),
      rules: z.boolean().refine((value) => !!value, {
        message: $t('authentication.agreeTip'),
      }),
    },
  ];
});

async function handleSubmit(value: Recordable<any>) {
  try {
    loading.value = true;

    // 1. 准备提交给后端的数据
    // 过滤掉 confirmPassword 和 agreePolicy，只发送后端需要的字段
    const params = {
      username: value.username,
      password: value.password,
      // 如果你的表单后续增加了 email 或 mobile，也可以在这里添加
    };

    // 2. 调用注册接口
    await registerApi(params);

    // 3. 注册成功提示
    ElMessage.success($t('authentication.registerSuccess') || '注册成功！');

    // 4. 跳转到登录页
    router.push('/auth/login');

  } catch (error: any) {
    // 错误处理：Vben 的 requestClient 通常会处理全局错误提示
    // 如果需要特殊处理，可以在这里捕获
    console.error('注册失败:', error);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <AuthenticationRegister
    :form-schema="formSchema"
    :loading="loading"
    @submit="handleSubmit"
  />
</template>
