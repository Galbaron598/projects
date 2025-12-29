import {
  HeartOutlined,
  ExperimentOutlined,
  ApiOutlined,
  UserOutlined,
  EyeOutlined,
  MedicineBoxOutlined,
} from '@ant-design/icons'

/**
 * Return a COMPONENT (not JSX), so callers render it like: <Icon />
 */
export const resolveMedicalIconComponent = (icon, name = '') => {
  const key = String(icon || name).toLowerCase().trim()

  if (key.includes('cardio') || key.includes('heart')) return HeartOutlined
  if (key.includes('neuro') || key.includes('brain') || key.includes('nerv')) return ExperimentOutlined
  if (key.includes('ortho') || key.includes('bone') || key.includes('joint')) return ApiOutlined
  if (key.includes('pedia') || key.includes('child') || key.includes('kids')) return UserOutlined
  if (key.includes('ophtha') || key.includes('eye') || key.includes('vision')) return EyeOutlined
  if (key.includes('general') || key.includes('medicine') || key.includes('primary')) return MedicineBoxOutlined

  return MedicineBoxOutlined
}