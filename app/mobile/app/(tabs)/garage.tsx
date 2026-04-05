// app/mobile/app/(tabs)/garage.tsx
import { useRouter } from "expo-router";
import { ScrollView, StyleSheet, View } from "react-native";
import EmptyState from "../../components/EmptyState";
import MotorcycleCard from "../../components/MotorcycleCard";
import ScreenHeader from "../../components/ScreenHeader";
import { useApp } from "../../context/AppContext";
import { colors, spacing } from "../../theme";

export default function GarageScreen() {
  const router = useRouter();
  const { motorcycles, setActiveMoto } = useApp();

  return (
    <View style={styles.container}>
      <ScreenHeader
        title="Garaj"
        rightAction={null}
      />

      {motorcycles.length === 0 ? (
        <EmptyState
          icon={"\u{1F527}"}
          title={"Garaj\u0131n Bo\u015F"}
          description={"\u0130lk motorunu ekleyerek ba\u015Fla."}
          actionLabel="+ Motor Ekle"
          onAction={() => router.push("/add-motorcycle")}
        />
      ) : (
        <ScrollView contentContainerStyle={styles.list} showsVerticalScrollIndicator={false}>
          {motorcycles.map((moto) => (
            <MotorcycleCard
              key={moto.id}
              motorcycle={moto}
              onPress={() => setActiveMoto(moto.id)}
            />
          ))}
          <View style={styles.addBtnWrap}>
            <EmptyState
              icon="+"
              title="Motor Ekle"
              description={"Garaj\u0131na yeni bir motor ekle"}
              actionLabel="+ Motor Ekle"
              onAction={() => router.push("/add-motorcycle")}
            />
          </View>
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  list: {
    paddingHorizontal: spacing.screenPadding,
    paddingBottom: 40,
    gap: 12,
  },
  addBtnWrap: { marginTop: 20, height: 200 },
});